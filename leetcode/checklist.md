# Checklist

- `reversed` goes in front of `range`, not after. `for i in reversed(range(n))`
- For binary search, use `while left <= right`:
  - When you can explicitly check if `mid` is the answer (e.g., `nums[mid] == target`)
  - Both branches eliminate `mid`: `left = mid + 1` and `right = mid - 1`
  - Return immediately when answer is found
- For binary search, use `while left < right`:
  - When you can't definitively test if `mid` is the answer
  - One branch keeps `mid` as a candidate: `right = mid` (or `left = mid`)
  - The other branch eliminates `mid`: `left = mid + 1` (or `right = mid - 1`)
  - Loop converges to single element when `left == right` — that's your answer
