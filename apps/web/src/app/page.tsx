export default function Home() {
  return (
    <main className="flex min-h-screen flex-col justify-center gap-6 px-8 py-10 sm:px-12">
      <div className="max-w-2xl">
        <p className="text-sm font-medium text-zinc-500">
          Phase 0 scaffold
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-normal text-zinc-950">
          Upbit Dashboard
        </h1>
        <p className="mt-4 text-base leading-7 text-zinc-600">
          Next.js frontend and FastAPI backend are ready for the health check
          flow.
        </p>
      </div>
      <div className="text-sm text-zinc-600">
        REST health proxy: <code className="font-mono">/api/health</code>
      </div>
      </main>
  );
}
