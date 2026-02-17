import { Button } from "@/components/ui/button";
import { Scale, MessageSquare, Shield, Zap, BookOpen } from "lucide-react";

const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-hero overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      <div className="absolute top-20 left-10 w-72 h-72 bg-secondary/20 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/20 rounded-full blur-3xl animate-pulse"></div>
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-5xl mx-auto text-center space-y-10 animate-fade-in">
          {/* Badge */}
          <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-gradient-card border border-secondary/30 backdrop-blur-sm shadow-glow">
            <Scale className="w-5 h-5 text-secondary" />
            <span className="text-sm font-medium text-primary-foreground">Legal AI Assistant</span>
          </div>
          
          {/* Main heading */}
          <h1 className="text-6xl md:text-8xl font-bold text-primary-foreground leading-tight tracking-tight">
            <span className="bg-gradient-accent bg-clip-text text-transparent">
              My Pocket Lawyer
            </span>
          </h1>
          
          {/* Subheading */}
          <p className="text-xl md:text-2xl text-primary-foreground/70 max-w-3xl mx-auto leading-relaxed">
            AI-Powered Legal Aid Assistant
          </p>
          
          {/* CTA Button */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-6">
            <Button
              size="lg"
              onClick={() => document.getElementById('chat-input')?.scrollIntoView({ behavior: 'smooth', block: 'center' })}
              className="group bg-gradient-accent hover:shadow-glow text-lg px-10 py-7 transition-all hover:scale-105 shadow-elevated"
            >
              Get Started
              <MessageSquare className="ml-2 group-hover:rotate-12 transition-transform" />
            </Button>
          </div>

        </div>
      </div>
      
      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 rounded-full border-2 border-primary-foreground/30 flex items-start justify-center p-2">
          <div className="w-1.5 h-1.5 rounded-full bg-primary-foreground/50"></div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
