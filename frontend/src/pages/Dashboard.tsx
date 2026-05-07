import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sprout, ArrowLeft, Search, FileText, Download, Eye, Loader2 } from "lucide-react";
import { fazendaOkApi, DiagnosticoResponse } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const Dashboard = () => {
  const [car, setCar] = useState("");
  const [historico, setHistorico] = useState<DiagnosticoResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (car.trim().length < 10) {
      toast({ title: "CAR inválido", description: "Informe o número completo.", variant: "destructive" });
      return;
    }

    setLoading(true);
    setHasSearched(true);
    try {
      const results = await fazendaOkApi.obterHistorico(car.trim());
      setHistorico(results);
    } catch (error: unknown) {
      const err = error as { response?: { status?: number } };
      if (err.response?.status === 404) {
        setHistorico([]);
      } else {
        toast({ title: "Erro na busca", description: "Não foi possível carregar o histórico.", variant: "destructive" });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = (id: string) => {
    toast({ title: "Gerando PDF", description: "Seu download começará em instantes." });
    const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/diagnostics/${id}/pdf`;
    window.open(url, "_blank");
  };

  const riskColors: Record<string, string> = {
    APTO: "bg-success text-success-foreground",
    RISCO_MEDIO: "bg-warning text-warning-foreground",
    RISCO_ALTO: "bg-orange-500 text-white",
    BLOQUEIO_PROVAVEL: "bg-danger text-danger-foreground",
    BLOQUEIO_DIRETO: "bg-red-900 text-white"
  };

  return (
    <div className="min-h-screen bg-gradient-soft font-sans text-foreground">
      <header className="border-b bg-background">
        <div className="container flex items-center justify-between py-4">
          <Link to="/" className="flex items-center gap-2 font-display font-extrabold text-primary">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-primary text-primary-foreground">
              <Sprout className="h-5 w-5" />
            </span>
            <span className="text-lg tracking-tight">FazendaOK</span>
          </Link>
          <Link to="/analise" className="text-sm text-muted-foreground hover:text-foreground inline-flex items-center gap-1.5">
            <ArrowLeft className="h-4 w-4" /> Nova Análise
          </Link>
        </div>
      </header>

      <main className="container py-10 md:py-16">
        <div className="max-w-5xl mx-auto">
          <h1 className="font-display text-3xl md:text-4xl font-extrabold leading-tight mb-8">
            Histórico de Diagnósticos
          </h1>

          <Card className="p-6 mb-8 shadow-card border-2 border-primary/5">
            <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4 items-end">
              <div className="w-full sm:flex-1">
                <label htmlFor="search-car" className="text-sm font-medium mb-1.5 block">Buscar por número do CAR</label>
                <div className="relative">
                  <FileText className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input 
                    id="search-car"
                    value={car}
                    onChange={(e) => setCar(e.target.value)}
                    placeholder="Ex: MT-5103403-E5F6..." 
                    className="pl-10 h-12 rounded-lg font-mono"
                  />
                </div>
              </div>
              <Button type="submit" disabled={loading} className="h-12 px-8 rounded-lg w-full sm:w-auto">
                {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <><Search className="mr-2 h-4 w-4" /> Buscar</>}
              </Button>
            </form>
          </Card>

          {hasSearched && !loading && historico.length === 0 && (
            <div className="text-center py-12 border-2 border-dashed rounded-xl bg-background">
              <p className="text-muted-foreground">Nenhum diagnóstico encontrado para o CAR informado.</p>
              <Link to="/analise">
                <Button variant="outline" className="mt-4">Realizar Nova Análise</Button>
              </Link>
            </div>
          )}

          {historico.length > 0 && (
            <div className="bg-background rounded-xl border shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="bg-muted/50 border-b">
                    <tr>
                      <th className="px-6 py-4 font-medium text-muted-foreground">Data da Análise</th>
                      <th className="px-6 py-4 font-medium text-muted-foreground">Risco Identificado</th>
                      <th className="px-6 py-4 font-medium text-muted-foreground">Área de Problema</th>
                      <th className="px-6 py-4 font-medium text-muted-foreground text-right">Ações</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {historico.map((diag) => (
                      <tr key={diag.id} className="hover:bg-muted/30 transition-colors">
                        <td className="px-6 py-4 font-medium">
                          {new Date(diag.created_at).toLocaleDateString('pt-BR')} às {new Date(diag.created_at).toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'})}
                        </td>
                        <td className="px-6 py-4">
                          <Badge className={`${riskColors[diag.risk_level] || 'bg-gray-200 text-gray-800'}`}>
                            {diag.risk_level.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td className="px-6 py-4">
                          {diag.problem_area_ha > 0 ? (
                            <span className="text-danger font-medium">{diag.problem_area_ha.toFixed(2)} ha</span>
                          ) : (
                            <span className="text-muted-foreground">0 ha</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-right space-x-2 whitespace-nowrap">
                          <Button size="sm" variant="outline" onClick={() => navigate(`/resultado/${diag.id}`)}>
                            <Eye className="h-4 w-4 mr-1.5" /> Ver
                          </Button>
                          <Button size="sm" onClick={() => handleDownloadPdf(diag.id)}>
                            <Download className="h-4 w-4 mr-1.5" /> PDF
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
