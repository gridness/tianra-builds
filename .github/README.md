# GitHub automation

[`gridness/tianra-builds`](https://github.com/gridness/tianra-builds) owns build,
check and promotion execution. All workflow definitions, helpers and tests live
under `.github/` in their respective repositories. Server publication and
deployment code stays under `apps/server/tools/`.

The private `Beta release` workflow pushes `requests/beta.json` to the public repo
after a push to private `main`. Its repository-scoped deploy key is stored in
`TIANRA_BUILDS_PUSH_KEY`. The request records source and comparison SHAs, run ID,
attempt and the original workflow run number. The public planner validates those
fields and private main ancestry before executing source code.

Preserve the private workflow name and path. Its run number plus the unchanged
`release.toml` offset identifies releases. Public workflow commits and counters
never identify player artifacts. Retrying the private workflow sends a new attempt
with the same release number. Failed public runs can also be retried directly.

`Checks` runs manually in the public repo against a selected private commit.
`Live promotion` remains manual there and accepts an activated Beta build.
Both production workflows share the public `tianra-production` concurrency group.

The public repo stores a read-only source deploy key, the existing encrypted
publication secrets and public configuration variables. Rotate deploy keys by
replacing both the repository key and the matching encrypted secret. Private source
is checked out on disposable public runners. Logs and caches are public; caches
exclude workspace build output and embedded media. Existing standard runner classes
and bounded caches remain within included public-repository allowances.

```sh
python3 -m unittest discover -s .github/tests -v
deno fmt --check .github/workflows
```
