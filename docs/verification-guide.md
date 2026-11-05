# Verification guide

Every entry starts as a **draft**: compiled from official pages, but not yet checked by a person.
Verifying entries is the most valuable thing a volunteer can do, and it makes a good research
project for students. It needs care and patience, not programming.

## What "verified" means

You personally opened every source page and confirmed that **every fact in the entry** matches it:
each phone number digit by digit, each link, each fee, each hour and each rule. Then you
recorded your GitHub handle and the date.

## Steps

1. **Pick a draft.** `uv run civic-atlas validate` lists counts; any file with
   `status: draft` is a candidate. Check open issues and pull requests so you don't duplicate
   someone else's work.
2. **Open each `source_urls` page** in your normal web browser.
3. **Check every channel.** Do the phone numbers match exactly? Does each link open the right
   page? Are hours current?
4. **Check the details:** fees, eligibility, deadlines, what to bring.
5. **Read the steps** and compare them with the real website or form. Look, but don't submit
   anything. If a step is wrong or unclear, rewrite it in your own words.
6. **Check the notes.** Are any discrepancies resolved? Update or remove those notes.
7. **Update provenance:**

   ```yaml
   provenance:
     source_urls: [...]          # add any better official page you found
     last_checked: 2026-11-15
     status: verified
     verified_by: your-github-handle
     verified_on: 2026-11-15
   ```

8. **Validate and open a pull request**, using the PR checklist. In the description, say what you
   checked and anything you changed.

## If something is wrong

Fix it if you can confirm the right answer from an official page. If you can't, set
`status: needs-review`, explain in `provenance.notes`, and open an issue.

## Don't

- Don't call or email a department just to verify (unless you're actually using the service),
  and never submit test requests.
- Don't mark an entry verified because it "looks right". Every fact must be checked.
- Don't use unofficial sites (news, blogs, AI answers) as sources. They can point you to the
  official page, but the official page is what gets cited.

## Re-verifying

Services change. `civic-atlas validate` warns about entries not checked in 180 days, and the
weekly link checker lists pages it couldn't reach. Re-verifying an old entry is just as useful as
verifying a new one.
