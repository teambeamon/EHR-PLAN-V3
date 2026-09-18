"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";

export default function MatchesPage() {
  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchMatches() {
      try {
        const response = await fetch('/api/matchs');
        if (!response.ok) {
          throw new Error('Failed to fetch matches');
        }
        const result = await response.json();
        setMatches(result.matchs || []);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch matches");
        setLoading(false);
      }
    }

    fetchMatches();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">Chargement des matchs...</div>
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
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Liste des Matchs
          </h1>
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium">
            Ajouter un match
          </button>
        </div>

        {matches.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
            <p className="text-gray-500 dark:text-gray-400">
              Aucun match trouvé
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {matches.map((match) => (
              <div
                key={match.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                        Match #{match.id}
                      </h2>
                      <p className="text-gray-600 dark:text-gray-400 mt-1">
                        {new Date(match.date).toLocaleString("fr-FR")}
                      </p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        match.statut === "terminé"
                          ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
                          : match.statut === "en cours"
                          ? "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
                          : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300"
                      }`}
                    >
                      {match.statut}
                    </span>
                  </div>

                  <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Salle
                      </p>
                      <p className="text-gray-900 dark:text-white">
                        {match.salle_nom} (Capacité: {match.salle_capacite})
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Équipes
                      </p>
                      <p className="text-gray-900 dark:text-white">
                        {match.equipe1 || "À définir"} vs {match.equipe2 || "À définir"}
                      </p>
                    </div>
                  </div>

                  <div className="mt-6 flex justify-end space-x-3">
                    <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700">
                      Détails
                    </button>
                    <button className="px-4 py-2 border border-indigo-600 text-indigo-600 rounded-md text-sm font-medium hover:bg-indigo-50 dark:hover:bg-indigo-900/30">
                      Éditer
                    </button>
                    <button className="px-4 py-2 border border-red-600 text-red-600 rounded-md text-sm font-medium hover:bg-red-50 dark:hover:bg-red-900/30">
                      Supprimer
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
