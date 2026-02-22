# Remove Cursor from GitHub contributors

If you still see **cursoragent** or **"Built by" Cursor** on your repo, do the following.

---

## Option A: Start completely from scratch (recommended)

This wipes all git history and creates **one commit** with only your identity.

1. **Close Cursor.** Open **PowerShell** from the Windows Start menu.
2. Run:

```powershell
cd "C:\Users\memet\OneDrive\Desktop\Autonomous Business Logic Orchestrator"
.\start_fresh.ps1
```

3. Then push:

```powershell
git push -u origin main --force
```

4. Hard-refresh the GitHub page (Ctrl+F5). You should see 1 commit and 1 contributor.

---

## Option B: Just fix the last commit (keep history)

## Step 1: Run the fix script OUTSIDE Cursor

Git in Cursor uses Cursor’s identity, so the fix must be run in a terminal that is **not** inside Cursor.

1. **Close Cursor** (or at least don’t use its terminal for this).
2. Press **Windows key**, type **PowerShell**, open **Windows PowerShell**.
3. Run:

```powershell
cd "C:\Users\memet\OneDrive\Desktop\Autonomous Business Logic Orchestrator"
.\fix_contributor.ps1
```

4. Then push:

```powershell
git push origin main --force
```

5. Open your repo on GitHub and do a **hard refresh** (Ctrl+F5). Contributors should show only you.

---

## Step 2: Remove Cursor’s access on GitHub

The **“Built by”** line and Cursor icon often come from Cursor’s connection to GitHub, not only from commit metadata.

1. Go to **https://github.com/settings/installations** (GitHub → your profile → Settings → Applications).
2. Find **Cursor** in the list.
3. Click **Configure** and either:
   - **Uninstall** Cursor, or  
   - **Limit** access so this repository is **not** selected.
4. Save.

Then refresh your repo page. The “Built by” Cursor badge may disappear.

---

## Step 3: Make sure future commits use your identity

In the same PowerShell (or any terminal outside Cursor), in your project folder:

```powershell
cd "C:\Users\memet\OneDrive\Desktop\Autonomous Business Logic Orchestrator"
git config user.name "mehmetalikosee"
git config user.email "mehmetalikosee@users.noreply.github.com"
```

After this, new commits you make from that machine will use your identity. If you use Cursor again and commit from inside Cursor, it may still use Cursor’s identity unless Cursor is configured to use your Git user name and email.
