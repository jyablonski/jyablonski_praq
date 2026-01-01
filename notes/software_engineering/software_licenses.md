## Open Source Software Licenses

Open-source licenses define the rules for using, modifying, and sharing software, and they aim to balance the freedom of users with the rights of creators.

- Permissive licenses intentionally encourage wide usage in open or closed source software and minimize legal friction for businesses and startups
- Copyleft licenses aim to protect the software, prevent closed-source forks, and encourage a "give-back" mentality for the project

| License | Can Use Commercially | Can Modify | Must Share Changes | Can Be Used in Closed Source | Copyleft Type | Notes |
| ---------------- | -------------------- | ---------- | ------------------------------- | ---------------------------- | ------------------------ | ---------------------------------------------------- |
| **MIT** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes | None | Very permissive. Simple. Common in startups. |
| **Apache 2.0** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes | None | Like MIT, but includes patent protection. |
| **BSD-3-Clause** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes | None | Similar to MIT. Often used in academic settings. |
| **GPLv3** | ✅ Yes | ✅ Yes | ✅ Yes (if distributed) | ❌ No | Strong copyleft | Any distributed code must be open-sourced under GPL. |
| **LGPLv3** | ✅ Yes | ✅ Yes | ✅ Yes (for libs only) | ✅ Yes (if dynamic linking) | Weak copyleft | Easier for proprietary use than GPL. For libraries. |
| **AGPLv3** | ✅ Yes | ✅ Yes | ✅ Yes (even over network) | ❌ No | Strong copyleft | Must open source changes **even if hosted** as SaaS. |
| **MPL 2.0** | ✅ Yes | ✅ Yes | ✅ Yes (for modified files) | ✅ Yes | File-level copyleft | Changes to individual files must be shared. |
| **EPL 2.0** | ✅ Yes | ✅ Yes | ✅ Yes (for modified components) | ✅ Yes | Component-level copyleft | Popular in enterprise (e.g. Eclipse projects). |

## Key Terms

- Can Use Commercially: You can use it in for-profit projects.

- Can Modify: You can alter the source code as needed.

- Must Share Changes: If you modify the code, are you required to publish those changes?

- Can Be Used in Closed Source: Can you integrate the code into proprietary software? (ex. prviate GitHub Repos)

- Copyleft Type:

  - None: You’re not required to share anything.
  - Weak: Share modifications only under specific conditions (e.g., LGPL for libraries).
  - Strong: You must open source all derivative works (e.g., GPL/AGPL).
  - File/Component-level: You must share only changes to the specific files/components you modify.
