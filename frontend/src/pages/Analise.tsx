import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import {
  Sprout, ArrowLeft, FileText, MapPin, Camera, Upload, X,
  Search, CheckCircle2, ShieldCheck, Satellite,
} from "lucide-react";

const Analise = () => {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [tab, setTab] = useState("car");

  // CAR
  const [car, setCar] = useState("");

  // Maps
  const [mapsUrl, setMapsUrl] = useState("");
  const [coords, setCoords] = useState("");
  const [address, setAddress] = useState("");

  // Fotos
  const [photos, setPhotos] = useState<{ file: File; url: string }[]>([]);
  const [notes, setNotes] = useState("");

  const handlePhotos = (files: FileList | null) => {
    if (!files) return;
    const accepted = Array.from(files)
      .filter((f) => f.type.startsWith("image/") && f.size <= 10 * 1024 * 1024)
      .slice(0, 10 - photos.length)
      .map((file) => ({ file, url: URL.createObjectURL(file) }));
    setPhotos((p) => [...p, ...accepted]);
  };

  const removePhoto = (i: number) => {
    setPhotos((p) => {
      URL.revokeObjectURL(p[i].url);
      return p.filter((_, idx) => idx !== i);
    });
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (tab === "car" && car.trim().length < 10) {
      toast({ title: "CAR inválido", description: "Informe o número completo do CAR.", variant: "destructive" });
      return;
    }
    if (tab === "maps" && !mapsUrl.trim() && !coords.trim() && !address.trim()) {
      toast({ title: "Informe a localização", description: "Cole o link do Google Maps, coordenadas ou endereço.", variant: "destructive" });
      return;
    }
    if (tab === "fotos" && photos.length === 0) {
      toast({ title: "Adicione fotos", description: "Envie pelo menos uma foto da propriedade.", variant: "destructive" });
      return;
    }
    toast({
      title: "Análise iniciada!",
      description: "Recebemos seus dados. Em breve você receberá o diagnóstico por e-mail.",
    });
    setTimeout(() => navigate("/"), 1500);
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
          <Link to="/" className="text-sm text-muted-foreground hover:text-foreground inline-flex items-center gap-1.5">
            <ArrowLeft className="h-4 w-4" /> Voltar
          </Link>
        </div>
      </header>

      <main className="container py-10 md:py-16">
        <div className="max-w-3xl mx-auto">
          <Badge variant="secondary" className="rounded-full mb-4">Passo 1 de 2 — Localizar fazenda</Badge>
          <h1 className="font-display text-3xl md:text-4xl font-extrabold leading-tight">
            Vamos encontrar sua propriedade
          </h1>
          <p className="mt-3 text-lg text-muted-foreground">
            Escolha a forma mais fácil para você. Quanto mais informações, mais preciso o diagnóstico.
          </p>

          <Card className="mt-8 p-6 md:p-8 shadow-card">
            <form onSubmit={submit}>
              <Tabs value={tab} onValueChange={setTab}>
                <TabsList className="grid grid-cols-3 w-full h-auto bg-muted p-1 rounded-xl">
                  <TabsTrigger value="car" className="rounded-lg py-2.5 data-[state=active]:bg-background">
                    <FileText className="h-4 w-4 mr-2 hidden sm:inline" /> CAR
                  </TabsTrigger>
                  <TabsTrigger value="maps" className="rounded-lg py-2.5 data-[state=active]:bg-background">
                    <MapPin className="h-4 w-4 mr-2 hidden sm:inline" /> Mapa
                  </TabsTrigger>
                  <TabsTrigger value="fotos" className="rounded-lg py-2.5 data-[state=active]:bg-background">
                    <Camera className="h-4 w-4 mr-2 hidden sm:inline" /> Fotos
                  </TabsTrigger>
                </TabsList>

                {/* CAR */}
                <TabsContent value="car" className="mt-6 space-y-4">
                  <div>
                    <Label htmlFor="car">Número do CAR</Label>
                    <Input
                      id="car"
                      value={car}
                      onChange={(e) => setCar(e.target.value)}
                      placeholder="Ex: SP-3550308-A1B2C3D4E5F6..."
                      className="mt-2 h-12 rounded-lg"
                      maxLength={60}
                    />
                    <p className="mt-2 text-sm text-muted-foreground">
                      Você encontra o número do CAR no recibo de inscrição. É a forma mais rápida e precisa.
                    </p>
                  </div>
                  <div className="rounded-lg bg-secondary/60 p-4 text-sm text-secondary-foreground">
                    Não tem o número em mãos? Use a aba <strong>Mapa</strong> ou <strong>Fotos</strong>.
                  </div>
                </TabsContent>

                {/* MAPS */}
                <TabsContent value="maps" className="mt-6 space-y-5">
                  <div>
                    <Label htmlFor="maps">Link do Google Maps</Label>
                    <div className="mt-2 flex gap-2">
                      <Input
                        id="maps"
                        value={mapsUrl}
                        onChange={(e) => setMapsUrl(e.target.value)}
                        placeholder="https://maps.google.com/..."
                        className="h-12 rounded-lg"
                        maxLength={500}
                      />
                      <a
                        href="https://www.google.com/maps"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="shrink-0"
                      >
                        <Button type="button" variant="outline" className="h-12 rounded-lg">
                          <Search className="h-4 w-4 mr-2" /> Abrir
                        </Button>
                      </a>
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Abra o Google Maps, encontre sua fazenda, clique com o botão direito e copie o link.
                    </p>
                  </div>

                  <div className="grid sm:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="coords">Coordenadas (lat, long)</Label>
                      <Input
                        id="coords"
                        value={coords}
                        onChange={(e) => setCoords(e.target.value)}
                        placeholder="-15.7942, -47.8822"
                        className="mt-2 h-12 rounded-lg"
                        maxLength={50}
                      />
                    </div>
                    <div>
                      <Label htmlFor="address">Endereço da propriedade</Label>
                      <Input
                        id="address"
                        value={address}
                        onChange={(e) => setAddress(e.target.value)}
                        placeholder="Município, estado, ponto de referência"
                        className="mt-2 h-12 rounded-lg"
                        maxLength={200}
                      />
                    </div>
                  </div>
                </TabsContent>

                {/* FOTOS */}
                <TabsContent value="fotos" className="mt-6 space-y-5">
                  <div>
                    <Label>Fotos da fazenda</Label>
                    <label className="mt-2 flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-border bg-secondary/30 p-8 cursor-pointer hover:border-primary/50 transition">
                      <div className="grid h-12 w-12 place-items-center rounded-full bg-primary/10 text-primary">
                        <Upload className="h-6 w-6" />
                      </div>
                      <div className="text-center">
                        <p className="font-medium">Toque para enviar fotos</p>
                        <p className="text-sm text-muted-foreground mt-1">
                          JPG ou PNG, até 10 MB cada. Máx. 10 fotos.
                        </p>
                      </div>
                      <input
                        type="file"
                        accept="image/*"
                        multiple
                        capture="environment"
                        className="hidden"
                        onChange={(e) => handlePhotos(e.target.files)}
                      />
                    </label>
                  </div>

                  {photos.length > 0 && (
                    <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
                      {photos.map((p, i) => (
                        <div key={i} className="relative aspect-square rounded-lg overflow-hidden border">
                          <img src={p.url} alt={`Foto ${i + 1}`} className="h-full w-full object-cover" />
                          <button
                            type="button"
                            onClick={() => removePhoto(i)}
                            aria-label="Remover foto"
                            className="absolute top-1 right-1 grid h-6 w-6 place-items-center rounded-full bg-foreground/70 text-background hover:bg-danger"
                          >
                            <X className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  <div>
                    <Label htmlFor="notes">Observações (opcional)</Label>
                    <Textarea
                      id="notes"
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="Pontos de referência, divisas, áreas de mata, açudes…"
                      className="mt-2 rounded-lg"
                      maxLength={1000}
                    />
                  </div>
                </TabsContent>
              </Tabs>

              <div className="mt-8 flex flex-col sm:flex-row gap-3">
                <Button
                  type="submit"
                  size="lg"
                  className="h-13 rounded-full bg-primary hover:bg-primary-glow font-semibold flex-1"
                >
                  Iniciar análise da fazenda
                </Button>
                <Link to="/" className="sm:w-auto">
                  <Button type="button" variant="outline" size="lg" className="h-13 rounded-full w-full">
                    Cancelar
                  </Button>
                </Link>
              </div>
            </form>
          </Card>

          <div className="mt-8 grid sm:grid-cols-3 gap-4 text-sm">
            <div className="flex items-start gap-2 text-muted-foreground">
              <ShieldCheck className="h-5 w-5 text-primary shrink-0" />
              Seus dados são usados apenas para a análise.
            </div>
            <div className="flex items-start gap-2 text-muted-foreground">
              <Satellite className="h-5 w-5 text-primary shrink-0" />
              Cruzamos com imagens de satélite oficiais.
            </div>
            <div className="flex items-start gap-2 text-muted-foreground">
              <CheckCircle2 className="h-5 w-5 text-success shrink-0" />
              Diagnóstico em até 48 horas.
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Analise;