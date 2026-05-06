import heroImg from "@/assets/hero-farm.jpg";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import {
  AlertTriangle, CheckCircle2, XCircle, Satellite, Sprout, ShieldCheck,
  MapPin, FileSearch, FileCheck2, Banknote, Clock, Database, Brain
} from "lucide-react";

const leadSchema = z.object({
  email: z.string().trim().email({ message: "Informe um e-mail válido" }).max(255),
});

const Index = () => {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const parsed = leadSchema.safeParse({ email });
    if (!parsed.success) {
      toast({ title: "Ops", description: parsed.error.issues[0].message, variant: "destructive" });
      return;
    }
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setEmail("");
      toast({ title: "Cadastro recebido!", description: "Agora vamos localizar sua fazenda." });
      navigate("/analise");
    }, 700);
  };

  return (
    <div className="min-h-screen bg-background font-sans text-foreground">
      {/* Nav */}
      <header className="absolute top-0 left-0 right-0 z-20">
        <div className="container flex items-center justify-between py-5">
          <a href="#" className="flex items-center gap-2 font-display font-extrabold text-primary-foreground">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-primary-foreground/15 backdrop-blur">
              <Sprout className="h-5 w-5" />
            </span>
            <span className="text-lg tracking-tight">FazendaOK</span>
          </a>
          <a href="#cta">
            <Button variant="secondary" className="rounded-full">Analisar agora</Button>
          </a>
        </div>
      </header>

      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0">
          <img
            src={heroImg}
            alt="Vista aérea de fazenda brasileira com demarcação do CAR"
            className="h-full w-full object-cover"
            width={1536}
            height={1024}
          />
          <div className="absolute inset-0 bg-gradient-hero opacity-95" />
        </div>

        <div className="container relative z-10 pt-32 pb-24 md:pt-40 md:pb-32">
          <Badge className="mb-6 rounded-full bg-warning/15 text-warning border-warning/30 hover:bg-warning/15">
            <AlertTriangle className="mr-1.5 h-3.5 w-3.5" /> Regra do crédito rural já em vigor desde 2026
          </Badge>

          <h1 className="font-display text-4xl md:text-6xl font-extrabold leading-[1.05] tracking-tight text-primary-foreground max-w-4xl">
            Descubra se sua fazenda será <span className="text-warning">bloqueada pelo banco</span> ANTES de pedir crédito
          </h1>
          <p className="mt-6 max-w-2xl text-lg md:text-xl text-primary-foreground/85">
            Evite perder a janela de plantio por problemas ambientais no CAR. Em minutos, saiba o risco real da sua propriedade.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row gap-3">
            <a href="#cta">
              <Button size="lg" className="h-14 px-8 rounded-full bg-warning text-earth hover:bg-warning/90 font-semibold text-base shadow-elegant">
                Analisar minha propriedade
              </Button>
            </a>
            <a href="#como">
              <Button size="lg" variant="outline" className="h-14 px-8 rounded-full bg-transparent border-primary-foreground/30 text-primary-foreground hover:bg-primary-foreground/10 hover:text-primary-foreground">
                Como funciona
              </Button>
            </a>
          </div>

          <div className="mt-10 flex flex-wrap gap-x-8 gap-y-3 text-sm text-primary-foreground/80">
            <span className="flex items-center gap-2"><Satellite className="h-4 w-4" /> Dados de satélite</span>
            <span className="flex items-center gap-2"><Database className="h-4 w-4" /> Bases oficiais do governo</span>
            <span className="flex items-center gap-2"><ShieldCheck className="h-4 w-4" /> Alinhado às exigências dos bancos</span>
          </div>
        </div>
      </section>

      {/* PROBLEMA */}
      <section className="py-20 md:py-28">
        <div className="container grid md:grid-cols-2 gap-12 items-center">
          <div>
            <Badge variant="secondary" className="rounded-full mb-4">O problema</Badge>
            <h2 className="font-display text-3xl md:text-4xl font-bold leading-tight">
              Uma irregularidade pode custar <span className="text-danger">sua safra inteira</span>
            </h2>
            <p className="mt-5 text-lg text-muted-foreground">
              Desde 2026, os bancos cruzam o CAR da sua propriedade com dados de satélite antes de liberar crédito rural.
              O problema? O produtor só descobre que há irregularidade <strong className="text-foreground">na hora de assinar o financiamento</strong> — quando já é tarde demais.
            </p>
            <ul className="mt-6 space-y-3 text-foreground">
              {[
                "Bancos cruzam o CAR com imagens de satélite",
                "Pedido de crédito pode ser bloqueado sem aviso",
                "Janela de plantio pode ser perdida em poucos dias",
              ].map((t) => (
                <li key={t} className="flex gap-3">
                  <XCircle className="h-5 w-5 text-danger shrink-0 mt-0.5" /> <span>{t}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Card className="p-6 shadow-card">
              <Clock className="h-8 w-8 text-danger" />
              <p className="mt-4 text-3xl font-display font-extrabold">+30 dias</p>
              <p className="text-sm text-muted-foreground mt-1">de atraso médio em pedidos com problema no CAR</p>
            </Card>
            <Card className="p-6 shadow-card mt-8">
              <Banknote className="h-8 w-8 text-danger" />
              <p className="mt-4 text-3xl font-display font-extrabold">R$ 500k+</p>
              <p className="text-sm text-muted-foreground mt-1">prejuízo médio de uma safra perdida</p>
            </Card>
            <Card className="p-6 shadow-card">
              <AlertTriangle className="h-8 w-8 text-warning" />
              <p className="mt-4 text-3xl font-display font-extrabold">1 em 3</p>
              <p className="text-sm text-muted-foreground mt-1">propriedades têm alguma divergência no CAR</p>
            </Card>
            <Card className="p-6 shadow-card mt-8">
              <Satellite className="h-8 w-8 text-primary" />
              <p className="mt-4 text-3xl font-display font-extrabold">100%</p>
              <p className="text-sm text-muted-foreground mt-1">das análises bancárias usam satélite</p>
            </Card>
          </div>
        </div>
      </section>

      {/* SOLUÇÃO */}
      <section className="py-20 md:py-28 bg-gradient-soft">
        <div className="container">
          <div className="max-w-2xl">
            <Badge variant="secondary" className="rounded-full mb-4">A solução</Badge>
            <h2 className="font-display text-3xl md:text-4xl font-bold leading-tight">
              O FazendaOK analisa sua propriedade <span className="text-primary">antes do banco</span>
            </h2>
            <p className="mt-5 text-lg text-muted-foreground">
              Você recebe um diagnóstico claro do risco da sua propriedade no crédito rural — e o que fazer para corrigir antes de pedir financiamento.
            </p>
          </div>

          <div className="mt-12 grid md:grid-cols-3 gap-5">
            <Card className="p-7 border-success/30 shadow-card">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-7 w-7 text-success" />
                <span className="font-display font-bold text-lg">Apto</span>
              </div>
              <p className="mt-3 text-muted-foreground">Sua propriedade está regular. Pode pedir crédito com segurança.</p>
            </Card>
            <Card className="p-7 border-warning/40 shadow-card">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-7 w-7 text-warning" />
                <span className="font-display font-bold text-lg">Risco médio</span>
              </div>
              <p className="mt-3 text-muted-foreground">Há pontos de atenção que podem atrasar o financiamento.</p>
            </Card>
            <Card className="p-7 border-danger/30 shadow-card">
              <div className="flex items-center gap-3">
                <XCircle className="h-7 w-7 text-danger" />
                <span className="font-display font-bold text-lg">Bloqueio provável</span>
              </div>
              <p className="mt-3 text-muted-foreground">Risco alto de recusa pelo banco. Mostramos o que corrigir primeiro.</p>
            </Card>
          </div>
        </div>
      </section>

      {/* COMO FUNCIONA */}
      <section id="como" className="py-20 md:py-28">
        <div className="container">
          <div className="text-center max-w-2xl mx-auto">
            <Badge variant="secondary" className="rounded-full mb-4">Como funciona</Badge>
            <h2 className="font-display text-3xl md:text-4xl font-bold">3 passos simples</h2>
          </div>

          <div className="mt-14 grid md:grid-cols-3 gap-6">
            {[
              { n: "01", icon: MapPin, t: "Informe sua propriedade", d: "Use o número do CAR ou as coordenadas da fazenda. Leva menos de 1 minuto." },
              { n: "02", icon: FileSearch, t: "Cruzamos os dados", d: "Comparamos seu CAR com imagens de satélite e bases oficiais do governo." },
              { n: "03", icon: FileCheck2, t: "Receba o diagnóstico", d: "Relatório simples mostrando o risco e o que fazer para liberar seu crédito." },
            ].map(({ n, icon: Icon, t, d }) => (
              <Card key={n} className="p-7 shadow-card relative overflow-hidden">
                <span className="absolute top-4 right-5 font-display text-5xl font-extrabold text-earth-light">{n}</span>
                <div className="grid h-12 w-12 place-items-center rounded-xl bg-primary text-primary-foreground">
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="mt-5 font-display text-xl font-bold">{t}</h3>
                <p className="mt-2 text-muted-foreground">{d}</p>
              </Card>
            ))}
          </div>

          <Card className="mt-12 p-8 md:p-10 bg-primary text-primary-foreground border-0 shadow-elegant">
            <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
              <div className="flex gap-3">
                <div className="grid h-12 w-12 place-items-center rounded-xl bg-primary-foreground/10">
                  <Brain className="h-6 w-6" />
                </div>
                <div className="grid h-12 w-12 place-items-center rounded-xl bg-primary-foreground/10">
                  <Satellite className="h-6 w-6" />
                </div>
              </div>
              <div>
                <h3 className="font-display text-xl md:text-2xl font-bold">Tecnologia simples para uma decisão complexa</h3>
                <p className="mt-2 text-primary-foreground/80">
                  Usamos dados oficiais e inteligência artificial para transformar informações complexas em um relatório que cabe em uma página.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* PROPOSTA DE VALOR + PREÇO */}
      <section className="py-20 md:py-28 bg-gradient-soft">
        <div className="container grid lg:grid-cols-2 gap-12 items-start">
          <div>
            <Badge variant="secondary" className="rounded-full mb-4">Por que usar</Badge>
            <h2 className="font-display text-3xl md:text-4xl font-bold leading-tight">
              Segurança antes de pedir crédito. Decisão com antecedência.
            </h2>
            <ul className="mt-8 space-y-5">
              {[
                { t: "Evite prejuízos de centenas de milhares", d: "Descubra problemas com tempo de corrigir, não na mesa do gerente." },
                { t: "Ganhe segurança no pedido de crédito", d: "Chegue ao banco sabendo exatamente o que vão analisar." },
                { t: "Tome decisão com antecedência", d: "Planeje sua safra com base em dados reais, não em achismo." },
              ].map((b) => (
                <li key={b.t} className="flex gap-4">
                  <div className="grid h-10 w-10 place-items-center rounded-full bg-success/15 shrink-0">
                    <CheckCircle2 className="h-5 w-5 text-success" />
                  </div>
                  <div>
                    <p className="font-display font-bold text-lg">{b.t}</p>
                    <p className="text-muted-foreground">{b.d}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <Card className="p-8 md:p-10 shadow-elegant border-2 border-primary/10">
            <Badge className="rounded-full bg-warning/15 text-earth border-0 hover:bg-warning/15">Modelo simples</Badge>
            <p className="mt-4 text-muted-foreground">Análise pontual</p>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="font-display text-2xl font-bold">A partir de</span>
              <span className="font-display text-5xl font-extrabold text-primary">R$ 99</span>
              <span className="text-muted-foreground">/análise</span>
            </div>
            <div className="my-8 h-px bg-border" />
            <p className="text-muted-foreground">Ou monitoramento contínuo</p>
            <p className="mt-1 font-display text-xl font-bold">Assinatura mensal</p>
            <p className="mt-2 text-muted-foreground">Receba alertas sempre que houver mudança que possa afetar seu crédito.</p>
            <a href="#cta" className="block mt-8">
              <Button size="lg" className="w-full h-13 rounded-full bg-primary hover:bg-primary-glow font-semibold">
                Começar análise
              </Button>
            </a>
            <p className="mt-4 text-xs text-center text-muted-foreground">
              Baseado em dados oficiais do governo • Alinhado às exigências dos bancos
            </p>
          </Card>
        </div>
      </section>

      {/* CTA FINAL */}
      <section id="cta" className="py-20 md:py-28">
        <div className="container">
          <Card className="overflow-hidden border-0 shadow-elegant">
            <div className="bg-gradient-hero p-8 md:p-14 text-primary-foreground">
              <Badge className="rounded-full bg-warning/20 text-warning border-warning/40 hover:bg-warning/20">
                <AlertTriangle className="mr-1.5 h-3.5 w-3.5" /> Não espere o banco descobrir
              </Badge>
              <h2 className="mt-5 font-display text-3xl md:text-5xl font-extrabold leading-tight max-w-3xl">
                Descubra agora o risco da sua propriedade
              </h2>
              <p className="mt-4 text-lg text-primary-foreground/85 max-w-2xl">
                Cadastre seu e-mail e receba o passo a passo para analisar sua fazenda antes do próximo pedido de crédito.
              </p>

              <form onSubmit={handleSubmit} className="mt-8 flex flex-col sm:flex-row gap-3 max-w-xl">
                <Input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu@email.com.br"
                  className="h-14 rounded-full bg-primary-foreground text-foreground border-0 px-6 text-base"
                  maxLength={255}
                />
                <Button
                  type="submit"
                  disabled={loading}
                  size="lg"
                  className="h-14 px-8 rounded-full bg-warning text-earth hover:bg-warning/90 font-semibold whitespace-nowrap"
                >
                  {loading ? "Enviando..." : "Quero analisar minha fazenda"}
                </Button>
              </form>
              <p className="mt-4 text-sm text-primary-foreground/70">
                Sem compromisso. Seu e-mail é usado apenas para entrar em contato sobre a análise.
              </p>
            </div>
          </Card>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t bg-muted/40">
        <div className="container py-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 font-display font-extrabold text-primary">
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary text-primary-foreground">
                <Sprout className="h-4 w-4" />
              </span>
              FazendaOK
            </div>
            <p className="mt-2 text-sm text-muted-foreground max-w-md">
              Análise de risco do CAR para crédito rural. Produto em desenvolvimento.
            </p>
          </div>
          <div className="text-sm text-muted-foreground">
            <p>Contato: <a href="mailto:contato@fazendaok.com.br" className="text-primary font-medium hover:underline">contato@fazendaok.com.br</a></p>
            <p className="mt-1">© {new Date().getFullYear()} FazendaOK • Em desenvolvimento</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
