import { useState, useEffect } from 'react';
import { 
  Trophy, 
  LayoutDashboard, 
  Flag, 
  Zap, 
  History, 
  Database, 
  LineChart, 
  Search, 
  RefreshCw,
  ChevronRight,
  Menu,
  X
} from 'lucide-react';

// --- Configuration & Data ---

const normalizeTeamKey = (name?: string) => (name || '').toLowerCase().replace(/[^a-z0-9]/g, '');

// Team icon mapping (normalized keys to public asset paths)
const TEAM_ICON_MAP = new Map<string, string>([
  ['mclaren', '/assets/TeamIcons/mclaren_icon.jpg'],
  ['ferrari', '/assets/TeamIcons/ferrari_icon.jpg'],
  ['williams', '/assets/TeamIcons/william_icon.jpg'],
  ['mercedes', '/assets/TeamIcons/amg_icon_update.jpg'],
  ['redbullracing', '/assets/TeamIcons/red_bull_icon.png'],
  ['redbull', '/assets/TeamIcons/red_bull_icon.png'],
  ['astonmartin', '/assets/TeamIcons/aston_martin_icon.webp'],
  ['kicksauber', '/assets/TeamIcons/kick_sauber_icon.png'],
  ['sauber', '/assets/TeamIcons/sauber_icon.png'],
  ['alpine', '/assets/TeamIcons/alpine_icon.png'],
  ['haasf1team', '/assets/TeamIcons/haas_icon.jpg'],
  ['haas', '/assets/TeamIcons/haas_icon.jpg'],
  ['racingbulls', '/assets/TeamIcons/VCARB_icon.jpg'],
  ['vcarb', '/assets/TeamIcons/VCARB_icon.jpg'],
  ['rb', '/assets/TeamIcons/VCARB_icon.jpg'],
  ['alphatauri', '/assets/TeamIcons/alpha_tauri_icon.png'],
  ['alphatauri', '/assets/TeamIcons/alpha_tauri_icon.png'],
  ['forceindia', '/assets/TeamIcons/force_india_icon.png'],
  ['racingpoint', '/assets/TeamIcons/Racing_point_icon.webp'],
  ['renault', '/assets/TeamIcons/renault_icon.webp'],
  ['tororosso', '/assets/TeamIcons/toro_rosso_icon.jpg'],
  ['alfaromeo', '/assets/TeamIcons/Alfa_Romeo_icon.webp'],
]);

const getTeamIcon = (team: any) => {
  const candidates = [team?.name, team?.full_name, team?.id];
  for (const candidate of candidates) {
    const icon = TEAM_ICON_MAP.get(normalizeTeamKey(candidate));
    if (icon) return icon;
  }
  return undefined;
};

const TEAMS_DATA = [
  {
    id: 'mclaren',
    name: 'McLaren',
    full_name: 'McLaren Formula 1 Team',
    rank: 1,
    points: 614,
    color: '#FF8000', // Papaya
    secondaryColor: '#1A1A1A',
    logo: 'https://upload.wikimedia.org/wikipedia/en/6/66/McLaren_Racing_logo.svg',
    drivers: [
      { name: 'Oscar Piastri', code: 'PIA', number: 81, points: 315, image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png' },
      { name: 'Lando Norris', code: 'NOR', number: 4, points: 299, image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png' }
    ]
  },
  {
    id: 'mercedes',
    name: 'Mercedes',
    full_name: 'Mercedes-AMG PETRONAS F1 Team',
    rank: 2,
    points: 311,
    color: '#00D2BE', // Petronas Cyan
    secondaryColor: '#C0C0C0',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/f/fb/Mercedes_AMG_Petronas_F1_Logo.svg',
    drivers: [
      { name: 'George Russell', code: 'RUS', number: 63, points: 227 },
      { name: 'Kimi Antonelli', code: 'ANT', number: 12, points: 84 }
    ]
  },
  {
    id: 'ferrari',
    name: 'Ferrari',
    full_name: 'Scuderia Ferrari HP',
    rank: 3,
    points: 275,
    color: '#DC0000', // Ferrari Red
    secondaryColor: '#FFF200',
    logo: 'https://upload.wikimedia.org/wikipedia/en/c/c0/Scuderia_Ferrari_Logo.svg',
    drivers: [
      { name: 'Charles Leclerc', code: 'LEC', number: 16, points: 164 },
      { name: 'Lewis Hamilton', code: 'HAM', number: 44, points: 111 }
    ]
  },
  {
    id: 'redbull',
    name: 'Red Bull Racing',
    full_name: 'Oracle Red Bull Racing',
    rank: 4,
    points: 273,
    color: '#061D42', // Navy
    secondaryColor: '#CC1E4A',
    logo: 'https://upload.wikimedia.org/wikipedia/en/c/c4/Red_Bull_Racing_logo.svg',
    drivers: [
      { name: 'Max Verstappen', code: 'VER', number: 1, points: 259 },
      { name: 'Liam Lawson', code: 'LAW', number: 30, points: 14 }
    ]
  },
  {
    id: 'williams',
    name: 'Williams',
    full_name: 'Williams Racing',
    rank: 5,
    points: 99,
    color: '#00A0DE', // Williams Blue
    secondaryColor: '#000000',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/e/e8/Williams_Racing_2020_logo.svg',
    drivers: [
      { name: 'Alexander Albon', code: 'ALB', number: 23, points: 70 },
      { name: 'Carlos Sainz', code: 'SAI', number: 55, points: 29 }
    ]
  },
  {
    id: 'vcarb',
    name: 'VCARB',
    full_name: 'Visa Cash App RB F1 Team',
    rank: 6,
    points: 68,
    color: '#1634CB', // VCARB Blue
    secondaryColor: '#FFFFFF',
    logo: 'https://upload.wikimedia.org/wikipedia/en/2/2b/VCARB_F1_logo.svg',
    drivers: [
      { name: 'Isack Hadjar', code: 'HAD', number: 6, points: 38 },
      { name: 'Yuki Tsunoda', code: 'TSU', number: 22, points: 30 }
    ]
  },
  {
    id: 'aston',
    name: 'Aston Martin',
    full_name: 'Aston Martin Aramco F1 Team',
    rank: 7,
    points: 64,
    color: '#006F62', // British Racing Green
    secondaryColor: '#CEDC00',
    logo: 'https://upload.wikimedia.org/wikipedia/en/b/bd/Aston_Martin_Lagonda_brand_logo.svg',
    drivers: [
      { name: 'Fernando Alonso', code: 'ALO', number: 14, points: 36 },
      { name: 'Lance Stroll', code: 'STR', number: 18, points: 28 }
    ]
  },
  {
    id: 'sauber',
    name: 'Kick Sauber',
    full_name: 'Stake F1 Team Kick Sauber',
    rank: 8,
    points: 55,
    color: '#52E252', // Neon Green
    secondaryColor: '#000000',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/4/47/Stake_F1_Team_Kick_Sauber_logo.svg',
    drivers: [
      { name: 'Nico Hulkenberg', code: 'HUL', number: 27, points: 37 },
      { name: 'Gabriel Bortoleto', code: 'BOR', number: 5, points: 18 }
    ]
  },
  {
    id: 'haas',
    name: 'Haas',
    full_name: 'MoneyGram Haas F1 Team',
    rank: 9,
    points: 40,
    color: '#B6BABD', // Grey/White
    secondaryColor: '#ED1A3B',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/d/d4/Haas_F1_Team_logo.svg',
    drivers: [
      { name: 'Esteban Ocon', code: 'OCO', number: 31, points: 24 },
      { name: 'Oliver Bearman', code: 'BEA', number: 87, points: 16 }
    ]
  },
  {
    id: 'alpine',
    name: 'Alpine',
    full_name: 'BWT Alpine F1 Team',
    rank: 10,
    points: 19,
    color: '#FD4BC7', // BWT Pink
    secondaryColor: '#0090FF',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/7/7e/Alpine_F1_Team_Logo.svg',
    drivers: [
      { name: 'Pierre Gasly', code: 'GAS', number: 10, points: 19 },
      { name: 'Jack Doohan', code: 'DOO', number: 7, points: 0 }
    ]
  }
];

// --- Components ---

const SidebarItem = ({ icon: Icon, label, active = false }: { icon: any, label: string, active?: boolean }) => (
  <button 
    className={`group flex items-center w-full p-3 rounded-xl mb-1 transition-all duration-300 ${
      active 
        ? 'bg-gradient-to-r from-red-600/20 to-transparent text-white border-l-2 border-red-500' 
        : 'text-slate-400 hover:text-white hover:bg-white/5'
    }`}
  >
    <Icon size={20} className={`mr-4 ${active ? 'text-red-500' : 'group-hover:text-red-400 transition-colors'}`} />
    <span className="font-medium tracking-wide text-sm uppercase">{label}</span>
  </button>
);

const DriverBar = ({ drivers, teamColor }: { drivers: any[], teamColor: string }) => {
  const totalPoints = drivers.reduce((acc, d) => acc + d.points, 0) || 1;
  const driver1Pct = (drivers[0].points / totalPoints) * 100;
  
  return (
    <div className="mt-4 space-y-2">
      <div className="flex justify-between text-xs text-slate-400 font-mono uppercase tracking-wider">
        <span>{drivers[0].code}</span>
        <span className="text-white/30">vs</span>
        <span>{drivers[1].code}</span>
      </div>
      <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex relative">
        <div 
          className="h-full relative group transition-all duration-1000 ease-out"
          style={{ width: `${driver1Pct}%`, backgroundColor: teamColor }}
        >
          {/* Shine effect */}
          <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
        </div>
        <div className="h-full flex-1 bg-slate-700/50" />
        
        {/* Divider Marker */}
        <div 
          className="absolute h-full w-0.5 bg-black/80 z-10" 
          style={{ left: `${driver1Pct}%` }} 
        />
      </div>
      <div className="flex justify-between text-[10px] text-slate-500 font-mono">
        <span>{drivers[0].points} PTS</span>
        <span>{drivers[1].points} PTS</span>
      </div>
    </div>
  );
};

const TeamCard = ({ team, isHero = false, delay = 0 }: { team: any, isHero?: boolean, delay?: number }) => {
  const [hovered, setHovered] = useState(false);
  const [mounted, setMounted] = useState(false);
  const icon = getTeamIcon(team);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  return (
    <div 
      className={`relative group rounded-3xl overflow-hidden backdrop-blur-md border border-white/10 transition-all duration-500 ease-out cursor-pointer ${
        mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      } ${isHero ? 'md:col-span-2 md:row-span-1' : ''} ${hovered ? 'transform -translate-y-2' : ''}`}
      style={{ 
        background: `linear-gradient(145deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.4) 100%)`,
        boxShadow: hovered ? `0 20px 40px -10px ${team.color}40` : '0 10px 20px -10px rgba(0,0,0,0.5)'
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Top Glow Border */}
      <div 
        className="absolute top-0 left-0 w-full h-[2px] transition-all duration-500"
        style={{ 
          background: `linear-gradient(90deg, transparent, ${team.color}, transparent)`,
          opacity: hovered ? 1 : 0.3
        }}
      />

      <div className="p-6 h-full flex flex-col justify-between relative z-10">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div className="flex items-center space-x-3">
             <div className="text-3xl font-bold text-white/10 font-mono -ml-1 select-none">
              P{team.rank}
             </div>
             <div>
                <h3 className="text-white font-bold text-lg tracking-wide uppercase italic">{team.name}</h3>
                <p className="text-slate-400 text-xs font-mono">{team.full_name}</p>
             </div>
          </div>
          
          {/* Circular Badge with Icon */}
          <div className="w-14 h-14 relative flex items-center justify-center rounded-full border-2 border-white/20 bg-white/5 backdrop-blur-sm overflow-hidden">
            <div 
              className="absolute inset-0 rounded-full opacity-30 blur-md" 
              style={{ backgroundColor: team.color }} 
            />
            {icon ? (
              <img 
                src={icon}
                alt={team.name}
                className="w-12 h-12 object-contain rounded-full relative z-10"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  const fallback = target.parentElement?.querySelector('.fallback-letter') as HTMLElement;
                  if (fallback) fallback.style.display = 'block';
                }}
              />
            ) : null}
            <div className="fallback-letter text-lg font-bold text-white relative z-10" style={{display: icon ? 'none' : 'block'}}>
              {team.name[0]}
            </div>
          </div>
        </div>

        {/* Hero-specific content */}
        {isHero && (
          <div className="my-6 hidden md:block">
            <div className="flex items-end space-x-2 mb-2">
              <span className="text-xs text-green-400 font-mono uppercase flex items-center">
                <Zap size={12} className="mr-1" />
                Trending Up
              </span>
              <div className="h-[1px] flex-1 bg-gradient-to-r from-green-500/50 to-transparent"></div>
            </div>
            {/* Fake sparkline using CSS bars */}
            <div className="flex items-end space-x-1 h-12 opacity-50">
                {[40, 65, 50, 80, 60, 90, 75, 100].map((h, i) => (
                    <div 
                        key={i} 
                        className="flex-1 bg-white/20 rounded-t-sm hover:bg-white/40 transition-colors"
                        style={{ height: `${h}%` }}
                    />
                ))}
            </div>
          </div>
        )}

        {/* Stats Section */}
        <div className="mt-6">
            <div className="flex items-baseline justify-between">
                <div>
                    <span className="text-xs text-slate-500 font-mono uppercase tracking-widest block mb-1">Total Points</span>
                    <span 
                        className="text-5xl font-light tracking-tighter text-white"
                        style={{ textShadow: hovered ? `0 0 20px ${team.color}40` : 'none' }}
                    >
                        {team.points}
                    </span>
                </div>
                {/* Visual Rank Indicator for non-heroes */}
                {!isHero && (
                     <div className="flex flex-col items-end">
                        <span className="text-xs text-slate-500 mb-1">Rank</span>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border border-white/10 ${team.rank <= 3 ? 'bg-white/10 text-white' : 'bg-slate-800 text-slate-400'}`}>
                            {team.rank}
                        </div>
                     </div>
                )}
            </div>

            <DriverBar drivers={team.drivers} teamColor={team.color} />
        </div>
      </div>
      
      {/* Background Gradient Texture */}
      <div 
        className="absolute inset-0 opacity-[0.03] z-0 pointer-events-none"
        style={{ 
            backgroundImage: `radial-gradient(circle at 100% 100%, ${team.color}, transparent 50%)`
        }}
      />
    </div>
  );
};

export default function TeamsView() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  
  // Handle scroll for navbar transparency
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-[#050505] text-slate-300 font-sans selection:bg-red-500 selection:text-white overflow-x-hidden">
      
      {/* --- Background Grid (F1 Technical Vibe) --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div 
            className="absolute inset-0" 
            style={{ 
                backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)',
                backgroundSize: '40px 40px'
            }} 
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#050505]/80 to-[#050505]" />
      </div>

      {/* --- Mobile Header --- */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-[#050505]/90 backdrop-blur-md z-50 flex items-center justify-between px-4 border-b border-white/5">
        <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-red-600 to-red-800 rounded flex items-center justify-center italic font-black text-white transform skew-x-[-10deg]">F1</div>
            <span className="font-bold text-white tracking-widest text-sm uppercase">Lakehouse</span>
        </div>
        <button onClick={() => setSidebarOpen(true)} className="p-2 text-white">
            <Menu size={24} />
        </button>
      </div>

      {/* --- Sidebar (Desktop) / Drawer (Mobile) --- */}
      <aside 
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#0a0a0a]/80 backdrop-blur-xl border-r border-white/5 transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="h-full flex flex-col p-6">
            {/* Brand */}
            <div className="flex items-center space-x-3 mb-10 pl-2">
                <div className="w-10 h-10 bg-gradient-to-br from-red-600 to-red-800 rounded flex items-center justify-center text-xl italic font-black text-white shadow-lg shadow-red-900/50 transform skew-x-[-10deg]">
                    L
                </div>
                <div>
                    <h1 className="font-bold text-white tracking-widest text-sm uppercase leading-tight">Lakehouse<br/><span className="text-red-500">Project</span></h1>
                </div>
                <button onClick={() => setSidebarOpen(false)} className="lg:hidden ml-auto text-slate-500">
                    <X size={20} />
                </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-1">
                <SidebarItem icon={LayoutDashboard} label="Home" />
                <SidebarItem icon={Flag} label="Standings" />
                <SidebarItem icon={Trophy} label="Teams" active />
                <SidebarItem icon={Search} label="Race Explorer" />
                <SidebarItem icon={Zap} label="Predictor" />
                <SidebarItem icon={History} label="History" />
                <div className="pt-6 pb-2">
                    <div className="text-xs font-mono text-slate-600 uppercase tracking-widest mb-4 px-3">Engineering</div>
                    <SidebarItem icon={Database} label="DE Monitor" />
                    <SidebarItem icon={LineChart} label="Skillset" />
                </div>
            </nav>

            {/* User Profile */}
            <div className="mt-auto pt-6 border-t border-white/5 flex items-center space-x-3 group cursor-pointer">
                <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-white font-bold border border-white/10 group-hover:border-red-500/50 transition-colors">
                    AD
                </div>
                <div>
                    <div className="text-sm font-bold text-white">Admin</div>
                    <div className="text-xs text-red-500 font-mono tracking-wide">ENGINEER</div>
                </div>
            </div>
        </div>
      </aside>

      {/* --- Main Content --- */}
      <main className="lg:ml-64 min-h-screen relative z-10 flex flex-col pt-20 lg:pt-0">
        
        {/* Top Bar */}
        <header className={`sticky top-0 z-40 px-8 py-4 flex items-center justify-between transition-all duration-300 ${
            scrolled ? 'bg-[#050505]/80 backdrop-blur-md border-b border-white/5' : 'bg-transparent'
        }`}>
            {/* Breadcrumbs / Context */}
            <div className="flex items-center space-x-4 text-sm font-mono tracking-wide">
                <span className="text-red-500 font-bold">2025 SEASON</span>
                <ChevronRight size={14} className="text-slate-600" />
                <span className="text-slate-300">SINGAPORE GRAND PRIX</span>
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse ml-4 shadow-[0_0_10px_#22c55e]"></span>
                <span className="text-xs text-green-500 hidden sm:inline-block">LIVE CONNECTION ACTIVE</span>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-4">
                <button className="flex items-center space-x-2 bg-white/5 hover:bg-white/10 text-xs font-bold uppercase tracking-widest text-white px-4 py-2 rounded border border-white/10 transition-colors">
                    <RefreshCw size={14} />
                    <span>Refresh Data</span>
                </button>
            </div>
        </header>

        {/* Content Body */}
        <div className="p-4 md:p-8 max-w-7xl mx-auto w-full">
            
            {/* Page Title */}
            <div className="mb-10 relative">
                <h1 className="text-5xl md:text-7xl font-black text-white uppercase italic tracking-tighter mb-2" style={{ textShadow: '0 0 40px rgba(255,255,255,0.1)' }}>
                    Teams
                </h1>
                <p className="text-slate-400 max-w-xl text-lg font-light">
                    Constructor championship telemetry and driver pairing performance analysis.
                </p>
                
                {/* Decorative Elements */}
                <div className="absolute -top-10 -right-10 w-64 h-64 bg-red-600/10 rounded-full blur-3xl pointer-events-none"></div>
                <div className="absolute top-20 left-40 w-96 h-96 bg-blue-600/5 rounded-full blur-3xl pointer-events-none"></div>
            </div>

            {/* Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                
                {/* --- Row 1: The Leaders (Bento Box Style) --- */}
                {/* P1 McLaren - Hero Card */}
                <TeamCard team={TEAMS_DATA[0]} isHero={true} delay={0} />
                
                {/* P2 Mercedes */}
                <TeamCard team={TEAMS_DATA[1]} delay={100} />
                
                {/* P3 Ferrari */}
                <TeamCard team={TEAMS_DATA[2]} delay={200} />

                {/* --- Row 2: The Midfield & Rest --- */}
                {/* Remaining teams map simply */}
                {TEAMS_DATA.slice(3).map((team, index) => (
                    <TeamCard key={team.id} team={team} delay={300 + (index * 50)} />
                ))}

            </div>
            
            <div className="mt-12 border-t border-white/5 pt-8 text-center">
                <p className="text-xs text-slate-600 font-mono">
                    LAKEHOUSE PROJECT // TELEMETRY MODULE V2.5 // DATA SOURCE: OFFICIAL F1 API
                </p>
            </div>
        </div>
      </main>
    </div>
  );
}
