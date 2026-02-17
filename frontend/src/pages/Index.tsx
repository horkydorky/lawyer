import Hero from "@/components/Hero";
import LegalAssistant from "@/components/LegalAssistant";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Hero />
      <LegalAssistant />
      
      <footer className="bg-gradient-hero text-primary-foreground py-12">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm opacity-80">
            © 2025 MyPocketLawyer. AI-powered legal assistance platform.
          </p>
          <p className="text-xs opacity-60 mt-2">
            Not a substitute for professional legal advice. Consult a licensed attorney for legal matters.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
