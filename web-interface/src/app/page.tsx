import Dashboard from './components/Dashboard';

export default function Home() {
  return (
    <body className="bg-gray-900">
      <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 md:p-12 lg:p-24">
        <Dashboard />
      </main>
    </body>
  );
}
