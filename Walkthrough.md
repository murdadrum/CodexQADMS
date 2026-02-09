# QADMS Web Walkthrough

1. Start local stack.
- Run `./scripts/run_local_stack.sh` from `/Users/murdadrum/QADMS`.

2. Open web app and sign in.
- Open `http://127.0.0.1:4173`.
- Use Google sign-in in Auth panel.
- Import/audit/report actions are gated when Firebase is configured.

3. Run first import + audit.
- In Import Request, keep defaults and click `Import Tokens`.
- Confirm provenance, validation, token summary, and violations render.

4. Export report.
- In Violations, click `Export Report JSON`.
- Confirm a report file downloads.

5. Save and apply filter preset.
- Set filters (severity/category/rule/search).
- Enter preset name and click `Save Preset`.
- Click preset chip to re-apply quickly.

6. Use recent-run drawer.
- In Recent Runs, click `Details` on any run.
- Confirm drawer metadata (source, time, API base, source, violations, validation, payload chars).
- Click `Load This Run` to restore source/API/payload into form.

7. Validate persistence.
- Refresh page.
- Confirm recent runs, presets, and filter state persist.
