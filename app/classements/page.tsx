"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import { createClient } from "@libsql/client";

export default function ClassementsPage() {
  const [classements, setClassements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchClassements() {
      try {
        const turso = createClient({
          url: process.env.NEXT_PUBLIC_TURSO_URL || "libsql://localhost",
          authToken: process.env.NEXT_PUBLIC_TURSO_AUTH_TOKEN,
        });

        const result = await turso.execute(
          `SELECT e.*, 
                  COUNT(m.id) as matchs_joues,
                  SUM(CASE WHEN m.gagnant_id = e.id THEN 1 ELSE 0 END) as victoires,
                  SUM(CASE WHEN m.gagnant_id != e.id AND m.gagnant_id IS NOT NULL THEN 1 ELSE 0 END) as défaites
           FROM équipes e 
           LEFT JOIN matchs m ON e.id = m.equipe1_id OR e.id = m.equipe2_id
           GROUP BY e.id, e.nom, e.logo
           ORDER BY victoires DESC, défaites ASC`
        );
        
        setClassements(result.rows as any[]);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch classements");
        setLoading(false);
      }
    }

    fetchClassements();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">Chargement des classements...</div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-100 dark:bg-red-900/30 p-4 rounded-md text-red-700 dark:text-red-300">
            Erreur: {error}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Classements
        </h1>

        {classements.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
            <p className="text-gray-500 dark:text-gray-400">
              Aucun classement disponible
            </p>
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <div className="p-6">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead>
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Rang
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Équipe
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Matchs joués
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Victoires
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Défaites
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Points
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {classements.map((equipe, index) => (
                    <tr key={equipe.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900 dark:text-white">
                        {index + 1}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {equipe.logo && (
                            <img
                              className="h-8 w-8 rounded-full mr-3"
                              src={equipe.logo}
                              alt={equipe.nom}
                            />
                          )}
                          <span className="text-sm font-medium text-gray-900 dark:text-white">
                            {equipe.nom}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {equipe.matchs_joues || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 dark:text-green-400 font-medium">
                        {equipe.victoires || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 dark:text-red-400 font-medium">
                        {equipe.defaites || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        {((equipe.victoires || 0) * 3) + ((equipe.defaites || 0) * 0)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
