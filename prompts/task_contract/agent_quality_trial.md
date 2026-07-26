# Agent Quality Trial Contract

## Goal

Implement exactly one bounded trial task against the provided synthetic-safe
fixture repository.

## Required Inputs

- task ID and trial ID
- base and contract-basis commits
- frozen paths
- read and write sets
- verification commands
- work-package plan digest
- safe approval reference

## Boundaries

- Change only the declared write set.
- Do not change frozen paths.
- Use the provided Python environment and repository-local dependencies only.
- Do not access network, remotes, later Git history, owner-held holdouts, private
  data, raw prompts, transcripts, memory, RAG, plugins, or skills.
- Do not push, open a pull request, dispatch a workflow, upload an artifact,
  release, deploy, or perform live action.
- Produce exactly one local commit.

## Closeout

Report only safe summaries: changed repo-relative paths, commit ID, focused test
status, postflight status, and unresolved reason codes. Do not report raw test
logs, source values, absolute paths, environment values, or prompt text.
