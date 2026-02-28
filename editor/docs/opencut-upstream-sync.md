# Elevo Editor Upstream Sync

## Initial fork import

```bash
git remote add opencut-upstream https://github.com/OpenCut-app/OpenCut.git
git fetch opencut-upstream main
git subtree add --prefix=apps/elevo-editor opencut-upstream main --squash
```

## Update from upstream

```bash
git fetch opencut-upstream main
git subtree pull --prefix=apps/elevo-editor opencut-upstream main --squash
```

## Local run

```bash
cd apps/elevo-editor
bun install
bun run dev:web
```

## Host-mode env required

- `NEXT_PUBLIC_FASTAPI_URL`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_SUPABASE_STORAGE_BUCKET`
- `NEXT_PUBLIC_EDITOR_BASE_PATH=/editor`
- `NEXT_PUBLIC_EDITOR_RETURN_TO=/editor`
- `NEXT_PUBLIC_EDITOR_DIAGNOSTICS=true|false`
