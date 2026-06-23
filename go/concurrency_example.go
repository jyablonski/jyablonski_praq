package main

import (
	"context"
	"errors"
	"sync"
)

func AURPKGBUILDRepos(
	ctx context.Context,
	cmdBuilder exe.GitCmdBuilder, logger *text.Logger,
	targets []string, aurURL, dest string, force bool,
) (map[string]bool, error) {
	// Return value: maps each package name -> was it a fresh clone (true)
	// vs. an already-existing repo we just updated (false).
	// len(targets) is a capacity hint so the map pre-allocates its buckets
	// and avoids growing/rehashing as we fill it. It's a hint, not a cap.
	cloned := make(map[string]bool, len(targets))

	// Shared state guarded across goroutines:
	//   mux  - serializes writes to cloned + errs (concurrent map writes panic;
	//          concurrent slice appends race silently).
	//   errs - collects per-target errors to join at the end.
	//   wg   - completion counter: lets us wait until every goroutine is done.
	var (
		mux  sync.Mutex
		errs []error
		wg   sync.WaitGroup
	)

	// Counting semaphore: a buffered channel acts as a bucket with
	// MaxConcurrentFetch slots. Sending takes a slot, receiving frees one.
	// This caps how many fetches run at once (and, since we acquire before
	// spawning, also caps how many goroutines are alive at once).
	sem := make(chan uint8, MaxConcurrentFetch)

	for _, target := range targets {
		// Acquire a slot BEFORE spawning. Blocks here once the bucket is full,
		// so the loop self-paces: it only spawns the next goroutine when a
		// running one finishes and frees a slot. Hovers at ~N alive.
		sem <- 1
		// Register one unit of total work. Must happen here in the main
		// goroutine (before the spawn) so the counter is already > 0 by the
		// time wg.Wait() runs — otherwise Wait could return prematurely.
		wg.Add(1)

		go func(target string) {
			// On exit (any path: error return or normal completion):
			//   <-sem    frees the slot so the loop can spawn the next one.
			//   wg.Done  decrements the completion counter toward zero.
			// defer guarantees both fire even on the early return below.
			defer func() {
				<-sem
				wg.Done()
			}()

			// The actual work — one git fetch/clone for this target.
			newClone, err := AURPKGBUILDRepo(ctx, cmdBuilder, aurURL, target, dest, force)

			// Enter the critical section to touch shared state. We read
			// progress under the lock so the count is consistent.
			mux.Lock()
			progress := len(cloned)
			if err != nil {
				// Record the failure, then UNLOCK before logging — we never
				// hold the mutex during I/O, or it'd serialize every log call.
				errs = append(errs, err)
				mux.Unlock()
				logger.OperationInfoln(
					gotext.Get("(%d/%d) Failed to download PKGBUILD: %s",
						progress, len(targets), text.Cyan(target)))
				return
			}

			// Success: record the result, re-read progress (now includes this
			// target), then unlock before logging — same discipline as above.
			cloned[target] = newClone
			progress = len(cloned)
			mux.Unlock()

			logger.OperationInfoln(
				gotext.Get("(%d/%d) Downloaded PKGBUILD: %s",
					progress, len(targets), text.Cyan(target)))
		}(target)
	}

	// Block until every spawned goroutine has called wg.Done(). Without this,
	// the function would return cloned while goroutines were still writing to
	// it — returning a half-filled map and racing on shared state.
	wg.Wait()

	// errors.Join collapses all collected errors into one (nil if errs empty).
	return cloned, errors.Join(errs...)
}
