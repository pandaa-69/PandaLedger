import React from 'react';
import { Github, Linkedin, Heart, Mail } from 'lucide-react'; // Added Mail for email contact
import { Link } from 'react-router-dom';

function Footer() {
  return (
    <footer className="w-full border-t border-white/10 bg-black py-12 text-center text-sm">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 px-6 md:flex-row">
        
        {/* 1. BRANDING */}
        <div className="flex flex-col items-center md:items-start">
          <Link to="/" className="flex items-center gap-2 group">
             <span className="text-2xl transition-transform group-hover:scale-110">🐼</span>
             <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 to-green-400 bg-clip-text text-transparent">
               PandaLedger
             </span>
          </Link>
          <p className="mt-2 text-gray-500">Your wealth, simplified.</p>
        </div>

        {/* 2. SOCIAL LINKS (Paste your real links here!) */}
        <div className="flex gap-4">
          
          {/* GitHub */}
          <SocialLink 
            icon={<Github size={18} />} 
            href="https://github.com/pandaa-69" 
          />
          
          {/* LinkedIn */}
          <SocialLink 
            icon={<Linkedin size={18} />} 
            href="https://www.linkedin.com/in/durgesh-kumar-3b79372b3/" 
          />

          {/* Email (Optional replacement for Twitter) */}
          <SocialLink 
            icon={<Mail size={18} />} 
            href="mailto:durgeshkumar070123@gmail.com" 
          />

        </div>
      </div>

      {/* 3. COPYRIGHT */}
      <div className="mt-10 flex items-center justify-center gap-1 text-gray-600">
        <span>© 2025 PandaLedger. Built by Durgesh (Panda) with</span>
        <Heart size={12} className="text-red-500 fill-red-500" />
        <span>and lots of ☕.</span>
      </div>
    </footer>
  );
}

const SocialLink = ({ icon, href }) => (
  <a 
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    className="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/5 text-gray-400 transition-all hover:scale-110 hover:bg-white/10 hover:text-white"
  >
    {icon}
  </a>
);

export default Footer;