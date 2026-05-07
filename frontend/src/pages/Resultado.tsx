import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sprout, ArrowLeft, Download, AlertTriangle, CheckCircle2, XCircle, Map as MapIcon, Info } from "lucide-react";
import { fazendaOkApi, DiagnosticoResponse } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const Resultado = () => {
  const { id } = useParams();
  const { toast } = useToast();
  const [diagnostico, setDiagnostico] = useState<DiagnosticoResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fazendaOkApi.obterDiagnostico(id)
        .then(setDiagnostico)
        .catch((err) => {
          console.error(err);
          toast({ title: "Erro", description: "Não foi possível carregar o diagnóstico.", variant: "destructive" });
        })
        .finally(() => setLoading(false));
    }
  }, [id, toast]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <Sprout className="h-12 w-12 text-primary mb-4" />
          <p className="text-muted-foreground">Carregando relatório...</p>
        </div>
      </div>
    );
  }

  if (!diagnostico) {
    return (
      <div className="min-h-screen flex items-center justify-center flex-col">
        <h2 className="text-2xl font-bold text-danger mb-2">Diagnóstico não encontrado</h2>
        <Link to="/analise"><Button>Voltar para Análise</Button></Link>
      </div>
    );
  }

  const riskColors: Record<string, string> = {
    APTO: "bg-success/20 text-success border-success/30",
    RISCO_MEDIO: "bg-warning/20 text-warning-foreground border-warning/30",
    RISCO_ALTO: "bg-orange-500/20 text-orange-600 border-orange-500/30",
    BLOQUEIO_PROVAVEL: "bg-danger/20 text-danger border-danger/30",
    BLOQUEIO_DIRETO: "bg-red-900/20 text-red-900 border-red-900/30"
  };
  
  const riskText: Record<string, string> = {
    APTO: "Apto para Crédito",
    RISCO_MEDIO: "Risco Médio",
    RISCO_ALTO: "Risco Alto",
    BLOQUEIO_PROVAVEL: "Bloqueio Provável",
    BLOQUEIO_DIRETO: "Bloqueio Direto"
  };

  const badgeStyle = riskColors[diagnostico.risk_level] || "bg-gray-100 text-gray-800";
  const badgeLabel = riskText[diagnostico.risk_level] || diagnostico.risk_level;

  const handleDownloadPdf = () => {
    toast({ title: "Gerando PDF", description: "Seu download começará em instantes." });
    // This assumes the backend has the endpoint available
    const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/diagnostics/${id}/pdf`;
    window.open(url, "_blank");
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
          <div className="flex gap-4">
            <Link to="/dashboard">
              <Button variant="ghost" className="text-muted-foreground">Meu Histórico</Button>
            </Link>
            <Link to="/analise" className="text-sm text-muted-foreground hover:text-foreground inline-flex items-center gap-1.5">
              <ArrowLeft className="h-4 w-4" /> Nova Análise
            </Link>
          </div>
        </div>
      </header>

      <main className="container py-10 md:py-16">
        <div className="max-w-4xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
            <div>
              <h1 className="font-display text-3xl md:text-4xl font-extrabold leading-tight">
                Resultado do Diagnóstico
              </h1>
              <p className="mt-2 text-muted-foreground">
                Análise gerada em {new Date(diagnostico.created_at).toLocaleDateString('pt-BR')}
              </p>
            </div>
            <Button onClick={handleDownloadPdf} className="shrink-0 gap-2">
              <Download className="h-4 w-4" /> Baixar PDF Oficial
            </Button>
          </div>

          <Card className="p-6 md:p-10 shadow-elegant border-2 border-primary/5">
            <div className="flex flex-col items-center text-center border-b pb-8">
              <Badge className={`px-4 py-1.5 text-sm md:text-base font-bold rounded-full mb-6 ${badgeStyle}`}>
                {badgeLabel}
              </Badge>
              
              <h2 className="text-xl md:text-2xl font-display font-bold">Parecer Técnico da IA</h2>
              <div className="mt-4 max-w-2xl text-left bg-muted/30 p-6 rounded-xl border whitespace-pre-wrap text-muted-foreground leading-relaxed">
                {diagnostico.llm_explanation}
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8 pt-8">
              <div>
                <h3 className="font-display text-lg font-bold flex items-center gap-2 mb-4">
                  <Info className="h-5 w-5 text-primary" /> Resumo Espacial
                </h3>
                <ul className="space-y-4">
                  <li className="flex justify-between border-b pb-2">
                    <span className="text-muted-foreground">Área Total da Propriedade</span>
                    <span className="font-medium">N/A ha</span> {/* Requereria join extra na API */}
                  </li>
                  <li className="flex justify-between border-b pb-2">
                    <span className="text-muted-foreground">Área de Problema (Sobreposição)</span>
                    <span className="font-medium text-danger">{diagnostico.problem_area_ha.toFixed(2)} ha</span>
                  </li>
                  <li className="flex justify-between border-b pb-2">
                    <span className="text-muted-foreground">Alertas PRODES Identificados</span>
                    <span className="font-medium">{diagnostico.prodes_alerts.length}</span>
                  </li>
                  <li className="flex justify-between pb-2">
                    <span className="text-muted-foreground">Alertas DETER (Últimos 24m)</span>
                    <span className="font-medium">{diagnostico.deter_alerts.length}</span>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="font-display text-lg font-bold flex items-center gap-2 mb-4">
                  <MapIcon className="h-5 w-5 text-primary" /> Visualização no Mapa
                </h3>
                <div className="aspect-video bg-muted rounded-xl border overflow-hidden relative flex items-center justify-center">
                  {/* Google Maps / Leaflet placeholder */}
                  {diagnostico.problem_geojson ? (
                    <div className="text-center p-4">
                      <MapIcon className="h-8 w-8 text-primary mx-auto opacity-50 mb-2" />
                      <p className="text-sm text-muted-foreground">Mapa com área de {diagnostico.problem_area_ha.toFixed(2)}ha destacada em vermelho.</p>
                      <Badge variant="outline" className="mt-2 bg-danger/10 text-danger border-danger/20">Área Problemática</Badge>
                    </div>
                  ) : (
                    <div className="text-center p-4">
                      <CheckCircle2 className="h-8 w-8 text-success mx-auto opacity-50 mb-2" />
                      <p className="text-sm text-muted-foreground">Nenhuma sobreposição ambiental encontrada no polígono desta fazenda.</p>
                    </div>
                  )}
                  {/* Se houvesse chave do Maps aqui renderizaríamos o componente */}
                </div>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                  A visualização exata requer configuração da chave de API do Google Maps.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default Resultado;
