"use client";

import { useState, useEffect } from "react";
import { createClient } from "@libsql/client";

export default function Home() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        // Initialize Turso client
        const turso = createClient({
          url: process.env.NEXT_PUBLIC_TURSO_URL || "libsql://localhost",
          authToken: process.env.NEXT_PUBLIC_TURSO_AUTH_TOKEN,
        });

        // Test connection
        const result = await turso.execute("SELECT * FROM salles LIMIT 10");
        setData(result.rows as any[]);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch data");
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) return <div className="p-8">Chargement...</div>;
  if (error) return <div className="p-8 text-red-500">Erreur: {error}</div>;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          EHR Plan - Accueil
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Salles</h2>
            <p>Gestion des salles disponibles</p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Planning</h2>
            <p>Visualisation du planning</p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Admin</h2>
            <p>Panneau d'administration</p>
          </div>
        </div>

        {data.length > 0 && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold mb-4">Données des salles</h2>
            <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        )}
      </main>
    </div>
  );
}
