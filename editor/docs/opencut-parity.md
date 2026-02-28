# Elevo Editor Parity Verification

## Verification gate (must pass before cutover)

1. Backend contract tests

```bash
cd backend
pytest tests/test_editor_elevo_editor_contract.py tests/test_editor_elevo_editor_storage.py -v
```

2. Existing editor project tests

```bash
cd backend
pytest tests/test_projects.py -v
```

3. Frontend integration checks

```bash
cd frontend
npm run test:editor-integration
```

## Manual checks

1. Login in Nuxt and open `/editor/:projectId`.
2. Confirm diagnostics panel (`?diag=1`) shows `projectId`, `userId`, save state, endpoint statuses.
3. Import video/image/audio and verify objects upload under:
   - `editor/assets/{userId}/{projectId}/{assetId}/{filename}`
4. Reload and verify timeline/media state round-trips without schema coercion.
5. Confirm `GET /api/v1/projects/{id}` returns `editor_engine=elevo-editor` and raw state version.

## Frame-accurate acceptance fixtures (legacy parity route)

Legacy fixture launcher route is now redirected at `frontend/pages/editor-legacy/parity-debug.vue`.
Use fixtures under `frontend/features/editor/fixtures/timeline/` for:
- adjacent transition crossfade
- one-frame gap no-transition
- short-clip transition clamp
- collision/snap checks
- long scrub drift
