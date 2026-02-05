"use client";

import React, { useEffect, useState } from "react";
import { fetchDashboardData, fetchIntel, reportScam, IntelItem } from '@/lib/api-client';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import clsx from 'clsx';
import { ShieldCheck, Activity, Database, Lock, Globe } from "lucide-react";

// Helper to safely extract text from message (handles string or object)
const getMessageText = (message: any): string => {
  if (typeof message === 'string') return message;
  if (typeof message === 'object' && message?.text) return message.text;
  return JSON.stringify(message || '');
};

export default function SOCDashboard() {
  const [interactions, setInteractions] = useState<any[]>([]);
  const [counts, setCounts] = useState<any>({});
  const [intelData, setIntelData] = useState<IntelItem[]>([]);
  const [isReporting, setIsReporting] = useState(false);

  // Poll for Dashboard Log every 3s
  useEffect(() => {
    const interval = setInterval(async () => {
      const data = await fetchDashboardData();
      if (data.interactions) setInteractions(data.interactions);
      if (data.turn_counts) setCounts(data.turn_counts);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // Poll for Intel Table every 3s
  useEffect(() => {
    const fetchTable = async () => {
      const data = await fetchIntel();
      setIntelData(data);
    };
    fetchTable(); // Initial load
    const interval = setInterval(fetchTable, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleReport = async () => {
    setIsReporting(true);
    const res = await reportScam();
    alert(res.message); // Simple feedback for Demo
    setIsReporting(false);
  };

  // --- Metrics Calculation ---
  const totalScammers = Object.keys(counts).length;
  const upiFlaggedCount = interactions.filter(i => i.extracted_intelligence?.upi_id).length;

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-white font-sans selection:bg-[#046A38] selection:text-white">
      {/* --- Navbar --- */}
      <header className="border-b border-white/10 bg-[#0a0f1e]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldCheck className="h-8 w-8 text-[#FF671F]" /> {/* Saffron */}
            <h1 className="text-xl font-bold tracking-wider uppercase bg-clip-text text-transparent bg-gradient-to-r from-[#FF671F] via-white to-[#046A38]">
              India AI Impact Summit 2026 - SOC
            </h1>
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-400">
            <span className="flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
              </span>
              Live Operations
            </span>
            <span className="border border-[#06038D] text-[#06038D] px-2 py-0.5 rounded text-xs bg-[#06038D]/10">
              DPDP Act 2023 Compliant
            </span>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 space-y-8">

        {/* --- Command Metrics Row --- */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-t-4 border-t-[#FF671F] bg-[#111827] border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">Scammers Engaged</CardTitle>
              <Activity className="h-4 w-4 text-[#FF671F]" />
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-white">{totalScammers}</div>
              <p className="text-xs text-gray-500 mt-1">Unique identities tracked</p>
            </CardContent>
          </Card>

          <Card className="border-t-4 border-t-[#046A38] bg-[#111827] border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">UPI IDs Flagged</CardTitle>
              <Database className="h-4 w-4 text-[#046A38]" />
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-white">{upiFlaggedCount}</div>
              <p className="text-xs text-gray-500 mt-1">Ready for NPCI Reporting</p>
            </CardContent>
          </Card>

          <Card className="border-t-4 border-t-[#06038D] bg-[#111827] border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">NPCI Integration</CardTitle>
              <Lock className="h-4 w-4 text-[#06038D]" />
            </CardHeader>
            <CardContent>
              <div className="text-xl font-bold text-[#00ff00]">SECURE LINK</div>
              <p className="text-xs text-gray-500 mt-1">Latency: 12ms</p>
            </CardContent>
          </Card>
        </div>

        {/* --- Main Content Grid --- */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* --- Left Col: Agent Feed (2/3 width) --- */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Activity className="h-5 w-5 text-blue-400" />
                Agent Intelligence Feed
              </h2>
            </div>

            <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
              {interactions.length === 0 ? (
                <div className="text-center py-10 text-gray-500">Waiting for live signals from honeypot...</div>
              ) : (
                interactions.map((interaction, idx) => (
                  <Card key={idx} className={clsx(
                    "border-l-4 mb-4",
                    interaction.scam_detected ? 'border-l-red-500 bg-red-900/10 border-red-900/20' : 'border-l-blue-500 bg-blue-900/10 border-blue-900/20'
                  )}>
                    <CardContent className="p-4 space-y-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <Badge variant={interaction.scam_detected ? "destructive" : "default"} className="mb-2">
                            {interaction.scam_detected ? "THREAT DETECTED" : "NORMAL TRAFFIC"}
                          </Badge>
                          <div className="text-xs text-gray-400 font-mono">{interaction.timestamp}</div>
                          <div className="text-xs text-gray-500 font-mono">ID: {interaction.client_id?.substring(0, 8)}...</div>
                        </div>
                        <Badge variant="outline" className={clsx(
                          interaction.suspicion_level === 'HIGH' ? 'text-red-400 border-red-400' :
                            interaction.suspicion_level === 'MEDIUM' ? 'text-yellow-400 border-yellow-400' :
                              'text-green-400 border-green-400'
                        )}>
                          SUSPICION: {interaction.suspicion_level}
                        </Badge>
                      </div>

                      {/* Reasoning Block */}
                      <div className="bg-black/40 p-3 rounded text-sm text-gray-300 font-mono border border-white/5">
                        <span className="text-blue-400 font-bold">ORCHESTRATOR:</span> {interaction.reasoning || "Analyzing conversation flow..."}
                      </div>

                      {/* Message Exchange */}
                      <div className="grid grid-cols-1 gap-2 text-sm">
                        <div className="text-red-300"><span className="font-bold opacity-70">TARGET:</span> "{getMessageText(interaction.message)}"</div>
                        <div className="text-green-300"><span className="font-bold opacity-70">MRS. SHARMA:</span> "{interaction.reply}"</div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </div>

          {/* --- Right Col: Map & Database (1/3 width) --- */}
          <div className="space-y-8">
            {/* --- Threat Pulse Map --- */}
            <Card className="overflow-hidden border-gray-800 bg-[#111827]">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-300 flex items-center gap-2">
                  <Globe className="h-4 w-4 text-blue-500" />
                  Live Threat Pulse Map
                </CardTitle>
              </CardHeader>
              <div className="relative h-64 bg-[#050a14] flex items-center justify-center p-4">
                {/* Abstract Map of India */}
                <svg viewBox="0 0 100 100" className="h-full w-full opacity-50">
                  <path d="M50,10 L60,30 L80,40 L70,70 L50,90 L30,70 L20,40 L40,30 Z" fill="none" stroke="#334155" strokeWidth="1" />

                  {/* Live Hotspots from Data */}
                  {Array.from(new Set(interactions.map(i => i.client_id))).map((id, uniqueIdx) => {
                    if (!id) return null;
                    // Deterministic hash to coordinate generator
                    const hash = id.split("").reduce((acc: number, char: string) => acc + char.charCodeAt(0), 0);
                    const x = 30 + (hash % 40);
                    const y = 30 + ((hash * 13) % 40);

                    return (
                      <g key={id}>
                        <circle cx={x} cy={y} r="3" fill="#FF671F" className="animate-ping opacity-75" style={{ animationDuration: '2s', animationDelay: `${uniqueIdx * 0.5}s` }} />
                        <circle cx={x} cy={y} r="1.5" fill="white" />
                      </g>
                    );
                  })}
                </svg>
                <div className="absolute bottom-2 right-2 text-[10px] text-green-500 flex items-center gap-1">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                  </span>
                  Live Feed Active
                </div>
              </div>
            </Card>

            {/* --- Intel Database --- */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <Database className="h-5 w-5 text-green-400" />
                  Intel Database
                </h2>
                <Button
                  size="sm"
                  variant="destructive"
                  className="bg-red-600 hover:bg-red-700 animate-pulse text-xs"
                  onClick={handleReport}
                  disabled={isReporting}
                >
                  {isReporting ? "Reporting..." : "Report to NPCI"}
                </Button>
              </div>

              <Card className="h-96 overflow-hidden flex flex-col border-gray-800 bg-[#111827]">
                <div className="p-4 border-b border-gray-800 bg-gray-900/50">
                  <div className="grid grid-cols-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    <div>Type</div>
                    <div>Value</div>
                    <div>Source</div>
                  </div>
                </div>
                <div className="overflow-y-auto p-4 space-y-2 flex-grow custom-scrollbar">
                  {intelData.length === 0 ? (
                    <div className="text-center text-gray-500 py-10 text-sm">No actionable intel extracted yet.</div>
                  ) : (
                    intelData.map((item, idx) => (
                      <div key={idx} className="grid grid-cols-3 text-sm py-2 border-b border-gray-800/50 last:border-0 hover:bg-blue-900/10 transition-colors">
                        <div>
                          <Badge variant="outline" className={clsx(
                            "text-[10px] w-fit",
                            item.type === 'UPI' && "border-yellow-500 text-yellow-500",
                            item.type === 'BANK' && "border-green-500 text-green-500",
                            item.type === 'LINK' && "border-red-500 text-red-500"
                          )}>{item.type}</Badge>
                        </div>
                        <div className="truncate pr-2 font-mono text-gray-300" title={item.value}>{item.value}</div>
                        <div className="truncate text-gray-500 text-xs" title={item.source}>{item.source ? item.source.substring(0, 8) + '...' : 'N/A'}</div>
                      </div>
                    ))
                  )}
                </div>
              </Card>
            </div>

          </div>
        </div>

        {/* --- Footer --- */}
        <footer className="mt-12 border-t border-gray-800 pt-6 text-center text-gray-500 text-sm">
          <p className="mb-2">Ministry of Electronics & IT - India AI Impact Summit 2026</p>
          <p>Protected System. Unauthorized Access is a punishable offense under IT Act, 2000.</p>
        </footer>
      </main>
    </div>
  );
}
