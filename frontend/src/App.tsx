/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState, useEffect, useMemo } from 'react';
import {
  Activity,
  Wind,
  Thermometer,
  Map as MapIcon,
  Zap,
  Database,
  Server,
  Code,
  Cpu,
  Trophy,
  Flag,
  ArrowRight,
  ChevronDown,
  // ChevronRight,
  Layers,
  Box,
  Calendar,
  Users,
  TrendingUp,
  PlayCircle,
  Settings,
  Droplets,
  X,
  History,
  Timer,
  Award,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import BahrainGpImage from '../../assets/GrandPrix Images/bahrain_gp.avif';
import SaudiGpImage from '../../assets/GrandPrix Images/saudi_gp.avif';
import AusGpImage from '../../assets/GrandPrix Images/aus_gp.avif';
import JapanGpImage from '../../assets/GrandPrix Images/japan_gp.avif';
import ChinaGpImage from '../../assets/GrandPrix Images/china_gp.avif';
import MiamiGpImage from '../../assets/GrandPrix Images/miami_gp.avif';
import ImolaGpImage from '../../assets/GrandPrix Images/emilia_Romagna_gp.avif';
import MonacoGpImage from '../../assets/GrandPrix Images/monoco_gp.png';
import CanadianGpImage from '../../assets/GrandPrix Images/canada_gp.png';
import SpainGpImage from '../../assets/GrandPrix Images/spanish_gp.png';
import AustriaGpImage from '../../assets/GrandPrix Images/austria_gp.avif';
import BritishGpImage from '../../assets/GrandPrix Images/british_gp.avif';
import HungaryGpImage from '../../assets/GrandPrix Images/hungarian_gp.png';
import BelgiumGpImage from '../../assets/GrandPrix Images/Belgium_gp.avif';
import DutchGpImage from '../../assets/GrandPrix Images/dutch_gp.png';
import ItalianGpImage from '../../assets/GrandPrix Images/Italy_gp.avif';
import AzerbaijanGpImage from '../../assets/GrandPrix Images/Baku_gp.avif';
import SingaporeGpImage from '../../assets/GrandPrix Images/singapor_gp.png';
import AustinGpImage from '../../assets/GrandPrix Images/US_gp.png';
import MexicoGpImage from '../../assets/GrandPrix Images/mexico_gp.png';
import SaoPauloGpImage from '../../assets/GrandPrix Images/brazil_gp.avif';
import LasVegasGpImage from '../../assets/GrandPrix Images/Las_Vegas_gp.avif';
import QatarGpImage from '../../assets/GrandPrix Images/quatar_gp.png';
import AbuDhabiGpImage from '../../assets/GrandPrix Images/Abu_Dhabi_gp.avif';
import RussiaGpImage from '../../assets/GrandPrix Images/Russia_gp.avif';
import FrenchGpImage from '../../assets/GrandPrix Images/french_gp.png';
import GermanGpImage from '../../assets/GrandPrix Images/German_gp.avif';
import AnniversaryGpImage from '../../assets/GrandPrix Images/70_gp.jpg';
import LandingHeroImage from '../../assets/Backround/main_bakcround_landing_Page.png';
import F1LakehouseLogo from './assets/f1lakehouse.png';

const API_BASE_URL =
  (import.meta as any)?.env?.VITE_API_BASE_URL ??
  'http://localhost:8000';

// Map track images by slug to keep visuals consistent
const TRACK_IMAGES: Record<string, string> = {
  'australian-grand-prix': AusGpImage,
  'japanese-grand-prix': JapanGpImage,
  'chinese-grand-prix': ChinaGpImage,
  'bahrain-grand-prix': BahrainGpImage,
  'saudi-arabian-grand-prix': SaudiGpImage,
  'miami-grand-prix': MiamiGpImage,
  'emilia-romagna-grand-prix': ImolaGpImage,
  'monaco-grand-prix': MonacoGpImage,
  'canadian-grand-prix': CanadianGpImage,
  'spanish-grand-prix': SpainGpImage,
  'austrian-grand-prix': AustriaGpImage,
  'british-grand-prix': BritishGpImage,
  'hungarian-grand-prix': HungaryGpImage,
  'belgian-grand-prix': BelgiumGpImage,
  'dutch-grand-prix': DutchGpImage,
  'italian-grand-prix': ItalianGpImage,
  'azerbaijan-grand-prix': AzerbaijanGpImage,
  'singapore-grand-prix': SingaporeGpImage,
  'united-states-grand-prix': AustinGpImage,
  'mexico-city-grand-prix': MexicoGpImage,
  'sao-paulo-grand-prix': SaoPauloGpImage,
  's-o-paulo-grand-prix': SaoPauloGpImage,
  'las-vegas-grand-prix': LasVegasGpImage,
  'qatar-grand-prix': QatarGpImage,
  'abu-dhabi-grand-prix': AbuDhabiGpImage,
  'mexican-grand-prix': MexicoGpImage,
  'brazilian-grand-prix': SaoPauloGpImage,
  'russian-grand-prix': RussiaGpImage,
  'french-grand-prix': FrenchGpImage,
  'german-grand-prix': GermanGpImage,
  'styrian-grand-prix': AustriaGpImage,
  '70th-anniversary-grand-prix': AnniversaryGpImage,
  'pre-season-testing': LandingHeroImage,
};

const TEAM_COLORS: Record<string, string> = {
  'Red Bull Racing': '#3671C6',
  'Ferrari': '#E8002D',
  'Mercedes': '#00D2BE',
  'McLaren': '#FF8000',
  'Aston Martin': '#229971',
  'RB': '#6692FF',
  'Racing Bulls': '#6692FF',
  'Alpine': '#FF87BC',
  'Kick Sauber': '#52E252',
  'Haas F1 Team': '#B6BABD',
  'Williams': '#64C4FF',
  'VCARB': '#6692FF',
  'Alfa Romeo': '#900000',
  'AlphaTauri': '#2B4562',
  'Alpha Tauri': '#2B4562',
  'Force India': '#FF9B9B',
  'Racing Point': '#F596C8',
  'Renault': '#FFF500',
  'Sauber': '#900000',
  'Toro Rosso': '#0032A0',
};

// Team icon mapping for standings page
const TEAM_ICONS: Record<string, string> = {
  'Ferrari': '/assets/TeamIcons/ferrari_icon.jpg',
  'Williams': '/assets/TeamIcons/william_icon.jpg',
  'McLaren': '/assets/TeamIcons/mclaren_icon.jpg',
  'Mercedes': '/assets/TeamIcons/amg_icon_update.jpg',
  'Red Bull Racing': '/assets/TeamIcons/red_bull_icon.png',
  'Aston Martin': '/assets/TeamIcons/aston_martin_icon.webp',
  'Kick Sauber': '/assets/TeamIcons/kick_sauber_icon.png',
  'Alpine': '/assets/TeamIcons/alpine_icon.png',
  'Racing Bulls': '/assets/TeamIcons/VCARB_icon.jpg',
  'VCARB': '/assets/TeamIcons/VCARB_icon.jpg',
  'Alfa Romeo': '/assets/TeamIcons/Alfa_Romeo_icon.webp',
  'AlphaTauri': '/assets/TeamIcons/alpha_tauri_icon.png',
  'Alpha Tauri': '/assets/TeamIcons/alpha_tauri_icon.png',
  'Force India': '/assets/TeamIcons/force_india_icon.png',
  'Racing Point': '/assets/TeamIcons/Racing_point_icon.webp',
  'Renault': '/assets/TeamIcons/renault_icon.webp',
  'Sauber': '/assets/TeamIcons/sauber_icon.png',
  'Toro Rosso': '/assets/TeamIcons/toro_rosso_icon.jpg',
  'Haas F1 Team': '/assets/TeamIcons/haas_icon.jpg',
};

// --- Types ---

type Driver = {
  id: string;
  name: string;
  team: string;
  number: number;
  color: string;
  points: number;
  image: string;
  country: string;
  careerWins: number;
  titles: number;
  poles: number;
  podiums: number;
  fastestLaps: number;
  grandPrix: number;
  rank?: number;
  seasonWins?: number;
  seasonPodiums?: number;
};

type Team = {
  id: string;
  name: string;
  fullTeamName: string;
  points: number;
  color: string;
  base: string;
  chief: string;
  powerUnit: string;
  titles: number;
  drivers: string[];
  isFuture?: boolean;
};

type Race = {
  season?: number;
  round: number;
  name: string;
  circuit: string;
  date: string;
  image: string;
  laps: number;
  length: string;
  trackId: string;
  rainProb: number;
  grandPrixSlug?: string;
};

type WeatherSummary = {
  rain?: number | null;
  trackTemp?: number | null;
  airTemp?: number | null;
  windSpeed?: number | null;
  humidity?: number | null;
};

// Backend-driven types
type RaceWinPrediction = {
  season: number;
  round: number;
  grand_prix_slug: string;
  driver_number?: number | null;
  driver_name?: string | null;
  driver_code?: string | null;
  team_name?: string | null;
  grid_position?: number | null;
  grid_position_norm?: number | null;
  driver_points_pre?: number | null;
  team_points_pre?: number | null;
  track_temp_c?: number | null;
  rain_probability?: number | null;
  driver_avg_finish_last_3?: number | null;
  driver_points_last_3?: number | null;
  team_points_last_3?: number | null;
  driver_track_avg_finish_last_3_at_gp?: number | null;
  driver_track_points_last_3_at_gp?: number | null;
  team_track_points_last_3_at_gp?: number | null;
  target_win_race?: number | null;
  pred_win_proba: number;
  pred_win_proba_softmax?: number | null;
};

type PredictionSummary = {
  season: number;
  n_races: number;
  n_wins: number;
  hit_at_1: number;
  hit_at_3: number;
};

type MonitorBronzeLatestSession = {
  season: number | null;
  round: number | null;
  grand_prix_slug?: string | null;
  session_code?: string | null;
  session_name?: string | null;
  date_start?: string | null;
};

type MonitorBronze = {
  n_sessions: number;
  n_seasons: number;
  n_result_rows?: number;
  latest_session?: MonitorBronzeLatestSession | null;
};

type MonitorPredictions = {
  season?: number | null;
  n_rows: number;
  n_races?: number | null;
};

type MonitorPayload = {
  bronze?: MonitorBronze | null;
  predictions?: MonitorPredictions | null;
  model?: PredictionSummary | null;
};

type RaceMeta = {
  season: number;
  round: number;
  grand_prix_slug: string;
  display_name: string;
  circuit_name?: string | null;
  date_start?: string | null;
  date_end?: string | null;
  display_round?: number;
};

type SessionMeta = {
  session_type: string;
  name: string;
  session_key: number;
};

type SessionResultRow = {
  position: number | null;
  driver_code: string | null;
  driver_name: string;
  team_name?: string | null;
  team_colour?: string | null;
  country_code?: string | null;
  grid?: number | null;
  laps?: number | null;
  points?: number | null;
  time_or_duration?: any;
  gap?: string | null;
  status?: string | null;
};

type DriverStanding = {
  position: number;
  driver_code: string;
  driver_name: string;
  team_name: string;
  points: number;
  wins: number;
  podiums: number;
};

type ConstructorStanding = {
  position: number;
  team_name: string;
  points: number;
};

type TeamStanding = {
  position: number;
  team_name: string;
  points: number;
  drivers: Array<{
    driver_code: string;
    driver_name: string;
    points: number;
    races: number;
  }>;
};

// History data types
type SeasonDriver = { name: string; points: number; image: string; wins: number; podiums: number; number?: number };
type SeasonTeam = {
  id: string;
  name: string;
  shortName: string;
  color: string;
  points: number;
  rank: number;
  carImage: string;
  drivers: SeasonDriver[];
  history?: number[];
};

const buildTrajectory = (team: SeasonTeam): number[] => {
  if (team.history && team.history.length) return team.history;
  const segments = 8;
  const step = Math.max(team.points / segments, 1);
  return Array.from({ length: segments }, (_, i) => Math.round(step * (i + 1)));
};
type SeasonData = {
  title: string;
  rounds: string;
  champion: string;
  championTeam: string;
  championColor: string;
  teams: SeasonTeam[];
};
type SeasonsDataMap = Record<number, SeasonData>;

type DriverPaceMap = Record<string, number[]>;
type RacePrediction = {
  season: number;
  round: number;
  driver_code: string | null;
  driver_name: string | null;
  team_name: string | null;
  pred_win_proba: number;
  pred_win_proba_softmax?: number | null;
  grid_position?: number | null;
};

const BattleBar: React.FC<{ label: string; v1: number; v2: number; max: number; color: string }> = ({ label, v1, v2, max, color }) => {
  const safeMax = max || 1;
  const w1 = (v1 / safeMax) * 100;
  const w2 = (v2 / safeMax) * 100;

  return (
    <div className="mb-4">
      <div className="mb-1 flex justify-center">
        <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-500">{label}</span>
      </div>
      <div className="flex items-center justify-center gap-4">
        <div className="flex flex-1 items-center justify-end gap-2">
          <span className="text-xs font-bold text-neutral-300 tabular-nums">{v1}</span>
          <div className="h-2 rounded-l-full bg-neutral-700 relative w-24 flex justify-end overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${w1}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className="h-full rounded-l-full"
              style={{ background: color }}
            />
          </div>
        </div>

        <div className="h-4 w-[1px] bg-neutral-600"></div>

        <div className="flex flex-1 items-center justify-start gap-2">
          <div className="h-2 rounded-r-full bg-neutral-700 relative w-24 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${w2}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className="h-full rounded-r-full bg-white"
            />
          </div>
          <span className="text-xs font-bold text-neutral-300 tabular-nums">{v2}</span>
        </div>
      </div>
    </div>
  );
};

// --- Mock Data ---


const DRIVER_CODE_LOOKUP: Record<string, string> = {
  verstappen: 'VER',
  perez: 'PER',
  norris: 'NOR',
  piastri: 'PIA',
  leclerc: 'LEC',
  hamilton: 'HAM',
  russell: 'RUS',
  antonelli: 'ANT',
  alonso: 'ALO',
  stroll: 'STR',
  albon: 'ALB',
  sainz: 'SAI',
  gasly: 'GAS',
  doohan: 'DOO',
  tsunoda: 'TSU',
  lawson: 'LAW',
  ricciardo: 'RIC',
  ocon: 'OCO',
  bearman: 'BEA',
  hulkenberg: 'HUL',
  bortoleto: 'BOR',
  colapinto: 'COL',
  zhou: 'ZHO',
  sargeant: 'SAR',
};

// Static lookup for images/colors; numeric stats will be replaced by API data in views.
const DRIVERS: Record<string, Driver> = {
  verstappen: { id: 'verstappen', name: 'Max Verstappen', team: 'Red Bull Racing', number: 1, color: '#3671C6', points: 0, country: 'NED', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  perez: { id: 'perez', name: 'Sergio Perez', team: 'Red Bull Racing', number: 11, color: '#3671C6', points: 0, country: 'MEX', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/S/SERPER01_Sergio_Perez/serper01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  norris: { id: 'norris', name: 'Lando Norris', team: 'McLaren', number: 4, color: '#FF8000', points: 0, country: 'GBR', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  piastri: { id: 'piastri', name: 'Oscar Piastri', team: 'McLaren', number: 81, color: '#FF8000', points: 0, country: 'AUS', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  leclerc: { id: 'leclerc', name: 'Charles Leclerc', team: 'Ferrari', number: 16, color: '#E8002D', points: 0, country: 'MON', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  hamilton: { id: 'hamilton', name: 'Lewis Hamilton', team: 'Ferrari', number: 44, color: '#E8002D', points: 0, country: 'GBR', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  russell: { id: 'russell', name: 'George Russell', team: 'Mercedes', number: 63, color: '#00D2BE', points: 0, country: 'GBR', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  antonelli: { id: 'antonelli', name: 'Kimi Antonelli', team: 'Mercedes', number: 12, color: '#00D2BE', points: 0, country: 'ITA', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/K/KIMANT01_Kimi_Antonelli/kimant01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  alonso: { id: 'alonso', name: 'Fernando Alonso', team: 'Aston Martin', number: 14, color: '#229971', points: 0, country: 'ESP', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/F/FERALO01_Fernando_Alonso/feralo01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  stroll: { id: 'stroll', name: 'Lance Stroll', team: 'Aston Martin', number: 18, color: '#229971', points: 0, country: 'CAN', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  albon: { id: 'albon', name: 'Alexander Albon', team: 'Williams', number: 23, color: '#64C4FF', points: 0, country: 'THA', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  sainz: { id: 'sainz', name: 'Carlos Sainz', team: 'Williams', number: 55, color: '#64C4FF', points: 0, country: 'ESP', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  colapinto: { id: 'colapinto', name: 'Franco Colapinto', team: 'Williams', number: 43, color: '#64C4FF', points: 0, country: 'ARG', image: 'https://media.formula1.com/content/dam/fom-website/drivers/F/FRACOL01_Franco_Colapinto/fracol01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  sargeant: { id: 'sargeant', name: 'Logan Sargeant', team: 'Williams', number: 2, color: '#64C4FF', points: 0, country: 'USA', image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LOGSAR01_Logan_Sargeant/logsar01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  gasly: { id: 'gasly', name: 'Pierre Gasly', team: 'Alpine', number: 10, color: '#FF87BC', points: 0, country: 'FRA', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  doohan: { id: 'doohan', name: 'Jack Doohan', team: 'Alpine', number: 19, color: '#FF87BC', points: 0, country: 'AUS', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/J/JACDOO01_Jack_Doohan/jacdoo01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  tsunoda: { id: 'tsunoda', name: 'Yuki Tsunoda', team: 'RB', number: 22, color: '#6692FF', points: 0, country: 'JPN', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/Y/YUKTSU01_Yuki_Tsunoda/yuktsu01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  lawson: { id: 'lawson', name: 'Liam Lawson', team: 'RB', number: 30, color: '#6692FF', points: 0, country: 'NZL', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LIALAW01_Liam_Lawson/lialaw01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  ricciardo: { id: 'ricciardo', name: 'Daniel Ricciardo', team: 'RB', number: 3, color: '#6692FF', points: 0, country: 'AUS', image: 'https://media.formula1.com/content/dam/fom-website/drivers/D/DANRIC01_Daniel_Ricciardo/danric01.png.transform/2col/image.png', careerWins: 8, titles: 0, poles: 3, podiums: 32, fastestLaps: 16, grandPrix: 200 },
  ocon: { id: 'ocon', name: 'Esteban Ocon', team: 'Haas', number: 31, color: '#B6BABD', points: 0, country: 'FRA', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/E/ESTOCO01_Esteban_Ocon/estoco01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  bearman: { id: 'bearman', name: 'Oliver Bearman', team: 'Haas', number: 87, color: '#B6BABD', points: 0, country: 'GBR', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OLIBEA01_Oliver_Bearman/olibea01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  magnussen: { id: 'magnussen', name: 'Kevin Magnussen', team: 'Haas', number: 20, color: '#B6BABD', points: 0, country: 'DNK', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/K/KEVMAG01_Kevin_Magnussen/kevmag01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  hulkenberg: { id: 'hulkenberg', name: 'Nico Hulkenberg', team: 'Kick Sauber', number: 27, color: '#52E252', points: 0, country: 'GER', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/N/NICHUL01_Nico_Hulkenberg/nichul01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  bortoleto: { id: 'bortoleto', name: 'Gabriel Bortoleto', team: 'Kick Sauber', number: 99, color: '#52E252', points: 0, country: 'BRA', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GABBOR01_Gabriel_Bortoleto/gabbor01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
  zhou: { id: 'zhou', name: 'Guanyu Zhou', team: 'Kick Sauber', number: 24, color: '#52E252', points: 0, country: 'CHN', image: 'https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GUAZHO01_Guanyu_Zhou/guazho01.png.transform/2col/image.png', careerWins: 0, titles: 0, poles: 0, podiums: 0, fastestLaps: 0, grandPrix: 0 },
};

const DRIVER_VISUAL_BY_CODE: Record<string, Driver> = Object.entries(DRIVERS).reduce((acc, [id, driver]) => {
  const code = DRIVER_CODE_LOOKUP[id];
  if (code) {
    acc[code.toUpperCase()] = driver;
  }
  return acc;
}, {} as Record<string, Driver>);

// --- Immutable Seasons Archive (do not modify values) ---
const SEASONS_DATA: SeasonsDataMap = {
  2018: {
    title: 'THE HAMILTON ERA',
    rounds: '21 / 21',
    champion: 'Lewis Hamilton',
    championTeam: 'Mercedes',
    championColor: '#00D2BE',
    teams: [
      { id: 'mer', name: 'Mercedes', shortName: 'MER', color: '#00D2BE', points: 655, rank: 1, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2018/mercedes.png', drivers: [{ name: 'Lewis Hamilton', points: 408, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/2col/image.png', wins: 11, podiums: 17 }, { name: 'Valtteri Bottas', points: 247, image: 'https://media.formula1.com/content/dam/fom-website/drivers/V/VALBOT01_Valtteri_Bottas/valbot01.png.transform/2col/image.png', wins: 0, podiums: 8 }] },
      { id: 'fer', name: 'Ferrari', shortName: 'FER', color: '#E80020', points: 571, rank: 2, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2018/ferrari.png', drivers: [{ name: 'Sebastian Vettel', points: 320, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SEBVET01_Sebastian_Vettel/sebvet01.png.transform/2col/image.png', wins: 5, podiums: 12 }, { name: 'Kimi Raikkonen', points: 251, image: 'https://media.formula1.com/content/dam/fom-website/drivers/K/KIMRAI01_Kimi_Räikkönen/kimrai01.png.transform/2col/image.png', wins: 1, podiums: 12 }] },
      { id: 'rbr', name: 'Red Bull Racing', shortName: 'RBR', color: '#0600EF', points: 419, rank: 3, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2018/red-bull-racing.png', drivers: [{ name: 'Max Verstappen', points: 249, image: 'https://media.formula1.com/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/2col/image.png', wins: 2, podiums: 11 }, { name: 'Daniel Ricciardo', points: 170, image: 'https://media.formula1.com/content/dam/fom-website/drivers/D/DANRIC01_Daniel_Ricciardo/danric01.png.transform/2col/image.png', wins: 2, podiums: 2 }] },
      { id: 'ren', name: 'Renault', shortName: 'REN', color: '#FFF500', points: 122, rank: 4, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2018/renault.png', drivers: [{ name: 'Nico Hulkenberg', points: 69, image: 'https://media.formula1.com/content/dam/fom-website/drivers/N/NICHUL01_Nico_Hulkenberg/nichul01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Carlos Sainz', points: 53, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'haa', name: 'Haas', shortName: 'HAA', color: '#B6BABD', points: 93, rank: 5, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2018/haas-f1-team.png', drivers: [{ name: 'Kevin Magnussen', points: 56, image: 'https://media.formula1.com/content/dam/fom-website/drivers/K/KEVMAG01_Kevin_Magnussen/kevmag01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Romain Grosjean', points: 37, image: 'https://media.formula1.com/content/dam/fom-website/drivers/R/ROMGRO01_Romain_Grosjean/romgro01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'mcl', name: 'McLaren', shortName: 'MCL', color: '#FF8000', points: 62, rank: 6, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2018/mclaren.png', drivers: [{ name: 'Fernando Alonso', points: 50, image: 'https://media.formula1.com/content/dam/fom-website/drivers/F/FERALO01_Fernando_Alonso/feralo01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Stoffel Vandoorne', points: 12, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/STOVAN01_Stoffel_Vandoorne/stovan01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'fi', name: 'Force India', shortName: 'RFI', color: '#F596C8', points: 52, rank: 7, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2018/force-india.png', drivers: [{ name: 'Sergio Perez', points: 62, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SERPER01_Sergio_Perez/serper01.png.transform/2col/image.png', wins: 0, podiums: 1 }, { name: 'Esteban Ocon', points: 49, image: 'https://media.formula1.com/content/dam/fom-website/drivers/E/ESTOCO01_Esteban_Ocon/estoco01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'sau', name: 'Sauber', shortName: 'SAU', color: '#9B0000', points: 48, rank: 8, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2018/sauber.png', drivers: [{ name: 'Charles Leclerc', points: 39, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Marcus Ericsson', points: 9, image: 'https://media.formula1.com/content/dam/fom-website/drivers/M/MARERI01_Marcus_Ericsson/mareri01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'tr', name: 'Toro Rosso', shortName: 'STR', color: '#0032FF', points: 33, rank: 9, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2018/toro-rosso.png', drivers: [{ name: 'Pierre Gasly', points: 29, image: 'https://media.formula1.com/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Brendon Hartley', points: 4, image: 'https://media.formula1.com/content/dam/fom-website/drivers/B/BREHAR01_Brendon_Hartley/brehar01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'wil', name: 'Williams', shortName: 'WIL', color: '#FFFFFF', points: 7, rank: 10, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2018/williams.png', drivers: [{ name: 'Lance Stroll', points: 6, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Sergey Sirotkin', points: 1, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SERSIR01_Sergey_Sirotkin/sersir01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
    ],
  },
  2019: {
    title: 'MERCEDES DOMINANCE',
    rounds: '21 / 21',
    champion: 'Lewis Hamilton',
    championTeam: 'Mercedes',
    championColor: '#00D2BE',
    teams: [
      { id: 'mer', name: 'Mercedes', shortName: 'MER', color: '#00D2BE', points: 739, rank: 1, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2019/mercedes.png', drivers: [{ name: 'Lewis Hamilton', points: 413, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/2col/image.png', wins: 11, podiums: 17 }, { name: 'Valtteri Bottas', points: 326, image: 'https://media.formula1.com/content/dam/fom-website/drivers/V/VALBOT01_Valtteri_Bottas/valbot01.png.transform/2col/image.png', wins: 4, podiums: 15 }] },
      { id: 'fer', name: 'Ferrari', shortName: 'FER', color: '#E80020', points: 504, rank: 2, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2019/ferrari.png', drivers: [{ name: 'Sebastian Vettel', points: 240, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SEBVET01_Sebastian_Vettel/sebvet01.png.transform/2col/image.png', wins: 1, podiums: 9 }, { name: 'Charles Leclerc', points: 264, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/2col/image.png', wins: 2, podiums: 10 }] },
      { id: 'rbr', name: 'Red Bull Racing', shortName: 'RBR', color: '#0600EF', points: 417, rank: 3, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2019/red-bull-racing.png', drivers: [{ name: 'Max Verstappen', points: 278, image: 'https://media.formula1.com/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/2col/image.png', wins: 3, podiums: 9 }, { name: 'Alex Albon', points: 92, image: 'https://media.formula1.com/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'mcl', name: 'McLaren', shortName: 'MCL', color: '#FF8000', points: 145, rank: 4, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2019/mclaren.png', drivers: [{ name: 'Carlos Sainz', points: 96, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png.transform/2col/image.png', wins: 0, podiums: 1 }, { name: 'Lando Norris', points: 49, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'ren', name: 'Renault', shortName: 'REN', color: '#FFF500', points: 91, rank: 5, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2019/renault.png', drivers: [{ name: 'Daniel Ricciardo', points: 54, image: 'https://media.formula1.com/content/dam/fom-website/drivers/D/DANRIC01_Daniel_Ricciardo/danric01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Nico Hulkenberg', points: 37, image: 'https://media.formula1.com/content/dam/fom-website/drivers/N/NICHUL01_Nico_Hulkenberg/nichul01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'tr', name: 'Toro Rosso', shortName: 'STR', color: '#0032FF', points: 85, rank: 6, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2019/toro-rosso.png', drivers: [{ name: 'Pierre Gasly', points: 95, image: 'https://media.formula1.com/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png.transform/2col/image.png', wins: 0, podiums: 1 }, { name: 'Daniil Kvyat', points: 37, image: 'https://media.formula1.com/content/dam/fom-website/drivers/D/DANKVY01_Daniil_Kvyat/dankvy01.png.transform/2col/image.png', wins: 0, podiums: 1 }] },
      { id: 'rp', name: 'Racing Point', shortName: 'RP', color: '#F596C8', points: 73, rank: 7, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2019/racing-point.png', drivers: [{ name: 'Sergio Perez', points: 52, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SERPER01_Sergio_Perez/serper01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Lance Stroll', points: 21, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'alf', name: 'Alfa Romeo', shortName: 'ALF', color: '#900000', points: 57, rank: 8, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2019/alfa-romeo-racing.png', drivers: [{ name: 'Kimi Raikkonen', points: 43, image: 'https://media.formula1.com/content/dam/fom-website/drivers/K/KIMRAI01_Kimi_Räikkönen/kimrai01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Antonio Giovinazzi', points: 14, image: 'https://media.formula1.com/content/dam/fom-website/drivers/A/ANTGIO01_Antonio_Giovinazzi/antgio01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'haa', name: 'Haas', shortName: 'HAA', color: '#B6BABD', points: 28, rank: 9, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2019/haas-f1-team.png', drivers: [{ name: 'Kevin Magnussen', points: 20, image: 'https://media.formula1.com/content/dam/fom-website/drivers/K/KEVMAG01_Kevin_Magnussen/kevmag01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Romain Grosjean', points: 8, image: 'https://media.formula1.com/content/dam/fom-website/drivers/R/ROMGRO01_Romain_Grosjean/romgro01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'wil', name: 'Williams', shortName: 'WIL', color: '#00A0DE', points: 1, rank: 10, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2019/williams.png', drivers: [{ name: 'George Russell', points: 0, image: 'https://media.formula1.com/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Robert Kubica', points: 1, image: 'https://media.formula1.com/content/dam/fom-website/drivers/R/ROBKUB01_Robert_Kubica/robkub01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
    ],
  },
  2020: {
    title: "HAMILTON'S 7TH",
    rounds: '17 / 17',
    champion: 'Lewis Hamilton',
    championTeam: 'Mercedes',
    championColor: '#00D2BE',
    teams: [
      { id: 'mer', name: 'Mercedes', shortName: 'MER', color: '#00D2BE', points: 573, rank: 1, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2020/mercedes.png', drivers: [{ name: 'Lewis Hamilton', points: 347, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/2col/image.png', wins: 11, podiums: 14 }, { name: 'Valtteri Bottas', points: 223, image: 'https://media.formula1.com/content/dam/fom-website/drivers/V/VALBOT01_Valtteri_Bottas/valbot01.png.transform/2col/image.png', wins: 2, podiums: 11 }] },
      { id: 'rbr', name: 'Red Bull Racing', shortName: 'RBR', color: '#0600EF', points: 319, rank: 2, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2020/red-bull-racing.png', drivers: [{ name: 'Max Verstappen', points: 214, image: 'https://media.formula1.com/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/2col/image.png', wins: 2, podiums: 11 }, { name: 'Alex Albon', points: 105, image: 'https://media.formula1.com/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png.transform/2col/image.png', wins: 0, podiums: 2 }] },
      { id: 'mcl', name: 'McLaren', shortName: 'MCL', color: '#FF8000', points: 202, rank: 3, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2020/mclaren.png', drivers: [{ name: 'Carlos Sainz', points: 105, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png.transform/2col/image.png', wins: 0, podiums: 1 }, { name: 'Lando Norris', points: 97, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png.transform/2col/image.png', wins: 0, podiums: 1 }] },
      { id: 'rp', name: 'Racing Point', shortName: 'RP', color: '#F596C8', points: 195, rank: 4, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2020/racing-point.png', drivers: [{ name: 'Sergio Perez', points: 125, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SERPER01_Sergio_Perez/serper01.png.transform/2col/image.png', wins: 1, podiums: 2 }, { name: 'Lance Stroll', points: 75, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png.transform/2col/image.png', wins: 0, podiums: 2 }] },
      { id: 'ren', name: 'Renault', shortName: 'REN', color: '#FFF500', points: 181, rank: 5, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2020/renault.png', drivers: [{ name: 'Daniel Ricciardo', points: 119, image: 'https://media.formula1.com/content/dam/fom-website/drivers/D/DANRIC01_Daniel_Ricciardo/danric01.png.transform/2col/image.png', wins: 0, podiums: 2 }, { name: 'Esteban Ocon', points: 62, image: 'https://media.formula1.com/content/dam/fom-website/drivers/E/ESTOCO01_Esteban_Ocon/estoco01.png.transform/2col/image.png', wins: 0, podiums: 1 }] },
      { id: 'fer', name: 'Ferrari', shortName: 'FER', color: '#E80020', points: 131, rank: 6, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2020/ferrari.png', drivers: [{ name: 'Charles Leclerc', points: 98, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/2col/image.png', wins: 0, podiums: 2 }, { name: 'Sebastian Vettel', points: 33, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SEBVET01_Sebastian_Vettel/sebvet01.png.transform/2col/image.png', wins: 0, podiums: 1 }] },
      { id: 'at', name: 'AlphaTauri', shortName: 'AT', color: '#FFFFFF', points: 107, rank: 7, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2020/alphatauri.png', drivers: [{ name: 'Pierre Gasly', points: 75, image: 'https://media.formula1.com/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png.transform/2col/image.png', wins: 1, podiums: 1 }, { name: 'Daniil Kvyat', points: 32, image: 'https://media.formula1.com/content/dam/fom-website/drivers/D/DANKVY01_Daniil_Kvyat/dankvy01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'alf', name: 'Alfa Romeo', shortName: 'ALF', color: '#900000', points: 8, rank: 8, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2020/alfa-romeo-racing.png', drivers: [{ name: 'Kimi Raikkonen', points: 4, image: 'https://media.formula1.com/content/dam/fom-website/drivers/K/KIMRAI01_Kimi_Räikkönen/kimrai01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Antonio Giovinazzi', points: 4, image: 'https://media.formula1.com/content/dam/fom-website/drivers/A/ANTGIO01_Antonio_Giovinazzi/antgio01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'haa', name: 'Haas', shortName: 'HAA', color: '#B6BABD', points: 3, rank: 9, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2020/haas-f1-team.png', drivers: [{ name: 'Romain Grosjean', points: 2, image: 'https://media.formula1.com/content/dam/fom-website/drivers/R/ROMGRO01_Romain_Grosjean/romgro01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Kevin Magnussen', points: 1, image: 'https://media.formula1.com/content/dam/fom-website/drivers/K/KEVMAG01_Kevin_Magnussen/kevmag01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'wil', name: 'Williams', shortName: 'WIL', color: '#005AFF', points: 0, rank: 10, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2020/williams.png', drivers: [{ name: 'George Russell', points: 3, image: 'https://media.formula1.com/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Nicholas Latifi', points: 0, image: 'https://media.formula1.com/content/dam/fom-website/drivers/N/NICLAT01_Nicholas_Latifi/niclat01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
    ],
  },
  2021: {
    title: 'THE TITLE FIGHT',
    rounds: '22 / 22',
    champion: 'Max Verstappen',
    championTeam: 'Red Bull Racing',
    championColor: '#0600EF',
    teams: [
      { id: 'mer', name: 'Mercedes', shortName: 'MER', color: '#00D2BE', points: 613, rank: 1, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2021/mercedes.png', drivers: [{ name: 'Lewis Hamilton', points: 387, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/2col/image.png', wins: 8, podiums: 17 }, { name: 'Valtteri Bottas', points: 226, image: 'https://media.formula1.com/content/dam/fom-website/drivers/V/VALBOT01_Valtteri_Bottas/valbot01.png.transform/2col/image.png', wins: 1, podiums: 11 }] },
      { id: 'rbr', name: 'Red Bull Racing', shortName: 'RBR', color: '#0600EF', points: 585, rank: 2, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2021/red-bull-racing.png', drivers: [{ name: 'Max Verstappen', points: 395, image: 'https://media.formula1.com/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/2col/image.png', wins: 10, podiums: 18 }, { name: 'Sergio Perez', points: 190, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SERPER01_Sergio_Perez/serper01.png.transform/2col/image.png', wins: 1, podiums: 5 }] },
      { id: 'fer', name: 'Ferrari', shortName: 'FER', color: '#E80020', points: 323, rank: 3, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2021/ferrari.png', drivers: [{ name: 'Charles Leclerc', points: 159, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/2col/image.png', wins: 0, podiums: 1 }, { name: 'Carlos Sainz', points: 164, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png.transform/2col/image.png', wins: 0, podiums: 4 }] },
      { id: 'mcl', name: 'McLaren', shortName: 'MCL', color: '#FF8000', points: 275, rank: 4, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2021/mclaren.png', drivers: [{ name: 'Lando Norris', points: 160, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png.transform/2col/image.png', wins: 0, podiums: 4 }, { name: 'Daniel Ricciardo', points: 115, image: 'https://media.formula1.com/content/dam/fom-website/drivers/D/DANRIC01_Daniel_Ricciardo/danric01.png.transform/2col/image.png', wins: 1, podiums: 1 }] },
      { id: 'alp', name: 'Alpine', shortName: 'ALP', color: '#0090FF', points: 155, rank: 5, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2021/alpine.png', drivers: [{ name: 'Fernando Alonso', points: 81, image: 'https://media.formula1.com/content/dam/fom-website/drivers/F/FERALO01_Fernando_Alonso/feralo01.png.transform/2col/image.png', wins: 0, podiums: 1 }, { name: 'Esteban Ocon', points: 74, image: 'https://media.formula1.com/content/dam/fom-website/drivers/E/ESTOCO01_Esteban_Ocon/estoco01.png.transform/2col/image.png', wins: 1, podiums: 1 }] },
      { id: 'at', name: 'AlphaTauri', shortName: 'AT', color: '#FFFFFF', points: 142, rank: 6, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2021/alphatauri.png', drivers: [{ name: 'Pierre Gasly', points: 110, image: 'https://media.formula1.com/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png.transform/2col/image.png', wins: 0, podiums: 1 }, { name: 'Yuki Tsunoda', points: 32, image: 'https://media.formula1.com/content/dam/fom-website/drivers/Y/YUKTSU01_Yuki_Tsunoda/yuktsu01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'ast', name: 'Aston Martin', shortName: 'AMR', color: '#006F62', points: 77, rank: 7, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2021/aston-martin.png', drivers: [{ name: 'Sebastian Vettel', points: 43, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SEBVET01_Sebastian_Vettel/sebvet01.png.transform/2col/image.png', wins: 0, podiums: 1 }, { name: 'Lance Stroll', points: 34, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'wil', name: 'Williams', shortName: 'WIL', color: '#005AFF', points: 23, rank: 8, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2021/williams.png', drivers: [{ name: 'George Russell', points: 16, image: 'https://media.formula1.com/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png.transform/2col/image.png', wins: 0, podiums: 1 }, { name: 'Nicholas Latifi', points: 7, image: 'https://media.formula1.com/content/dam/fom-website/drivers/N/NICLAT01_Nicholas_Latifi/niclat01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'alf', name: 'Alfa Romeo', shortName: 'ALF', color: '#900000', points: 13, rank: 9, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2021/alfa-romeo-racing.png', drivers: [{ name: 'Kimi Raikkonen', points: 10, image: 'https://media.formula1.com/content/dam/fom-website/drivers/K/KIMRAI01_Kimi_Räikkönen/kimrai01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Antonio Giovinazzi', points: 3, image: 'https://media.formula1.com/content/dam/fom-website/drivers/A/ANTGIO01_Antonio_Giovinazzi/antgio01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'haa', name: 'Haas', shortName: 'HAA', color: '#B6BABD', points: 0, rank: 10, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2021/haas-f1-team.png', drivers: [{ name: 'Mick Schumacher', points: 0, image: 'https://media.formula1.com/content/dam/fom-website/drivers/M/MICSCH02_Mick_Schumacher/micsch02.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Nikita Mazepin', points: 0, image: 'https://media.formula1.com/content/dam/fom-website/drivers/N/NIKMAZ01_Nikita_Mazepin/nikmaz01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
    ],
  },
  2022: {
    title: "MAX'S DOMINANCE",
    rounds: '22 / 22',
    champion: 'Max Verstappen',
    championTeam: 'Red Bull Racing',
    championColor: '#0600EF',
    teams: [
      { id: 'rbr', name: 'Red Bull Racing', shortName: 'RBR', color: '#0600EF', points: 759, rank: 1, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2022/red-bull-racing.png', drivers: [{ name: 'Max Verstappen', points: 454, image: 'https://media.formula1.com/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/2col/image.png', wins: 15, podiums: 17 }, { name: 'Sergio Perez', points: 305, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SERPER01_Sergio_Perez/serper01.png.transform/2col/image.png', wins: 2, podiums: 11 }] },
      { id: 'fer', name: 'Ferrari', shortName: 'FER', color: '#E80020', points: 554, rank: 2, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2022/ferrari.png', drivers: [{ name: 'Charles Leclerc', points: 308, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/2col/image.png', wins: 3, podiums: 11 }, { name: 'Carlos Sainz', points: 246, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png.transform/2col/image.png', wins: 1, podiums: 9 }] },
      { id: 'mer', name: 'Mercedes', shortName: 'MER', color: '#00D2BE', points: 515, rank: 3, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2022/mercedes.png', drivers: [{ name: 'George Russell', points: 275, image: 'https://media.formula1.com/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png.transform/2col/image.png', wins: 1, podiums: 8 }, { name: 'Lewis Hamilton', points: 240, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/2col/image.png', wins: 0, podiums: 9 }] },
      { id: 'alp', name: 'Alpine', shortName: 'ALP', color: '#0090FF', points: 173, rank: 4, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2022/alpine.png', drivers: [{ name: 'Esteban Ocon', points: 92, image: 'https://media.formula1.com/content/dam/fom-website/drivers/E/ESTOCO01_Esteban_Ocon/estoco01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Fernando Alonso', points: 81, image: 'https://media.formula1.com/content/dam/fom-website/drivers/F/FERALO01_Fernando_Alonso/feralo01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'mcl', name: 'McLaren', shortName: 'MCL', color: '#FF8000', points: 159, rank: 5, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2022/mclaren.png', drivers: [{ name: 'Lando Norris', points: 122, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png.transform/2col/image.png', wins: 0, podiums: 1 }, { name: 'Daniel Ricciardo', points: 37, image: 'https://media.formula1.com/content/dam/fom-website/drivers/D/DANRIC01_Daniel_Ricciardo/danric01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'alf', name: 'Alfa Romeo', shortName: 'ALF', color: '#900000', points: 55, rank: 6, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2022/alfa-romeo-racing.png', drivers: [{ name: 'Valtteri Bottas', points: 49, image: 'https://media.formula1.com/content/dam/fom-website/drivers/V/VALBOT01_Valtteri_Bottas/valbot01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Zhou Guanyu', points: 6, image: 'https://media.formula1.com/content/dam/fom-website/drivers/G/GUAZHO01_Zhou_Guanyu/guazho01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'ast', name: 'Aston Martin', shortName: 'AMR', color: '#006F62', points: 55, rank: 7, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2022/aston-martin.png', drivers: [{ name: 'Sebastian Vettel', points: 37, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SEBVET01_Sebastian_Vettel/sebvet01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Lance Stroll', points: 18, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'haa', name: 'Haas', shortName: 'HAA', color: '#B6BABD', points: 37, rank: 8, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2022/haas-f1-team.png', drivers: [{ name: 'Kevin Magnussen', points: 25, image: 'https://media.formula1.com/content/dam/fom-website/drivers/K/KEVMAG01_Kevin_Magnussen/kevmag01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Mick Schumacher', points: 12, image: 'https://media.formula1.com/content/dam/fom-website/drivers/M/MICSCH02_Mick_Schumacher/micsch02.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'at', name: 'AlphaTauri', shortName: 'AT', color: '#FFFFFF', points: 35, rank: 9, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2022/alphatauri.png', drivers: [{ name: 'Pierre Gasly', points: 23, image: 'https://media.formula1.com/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Yuki Tsunoda', points: 12, image: 'https://media.formula1.com/content/dam/fom-website/drivers/Y/YUKTSU01_Yuki_Tsunoda/yuktsu01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'wil', name: 'Williams', shortName: 'WIL', color: '#005AFF', points: 8, rank: 10, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2022/williams.png', drivers: [{ name: 'Alex Albon', points: 4, image: 'https://media.formula1.com/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Nicholas Latifi', points: 2, image: 'https://media.formula1.com/content/dam/fom-website/drivers/N/NICLAT01_Nicholas_Latifi/niclat01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
    ],
  },
  2023: {
    title: 'THE RB19 MASTERCLASS',
    rounds: '22 / 22',
    champion: 'Max Verstappen',
    championTeam: 'Red Bull Racing',
    championColor: '#0600EF',
    teams: [
      { id: 'rbr', name: 'Red Bull Racing', shortName: 'RBR', color: '#0600EF', points: 860, rank: 1, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2023/red-bull-racing.png', drivers: [{ name: 'Max Verstappen', points: 575, image: 'https://media.formula1.com/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/2col/image.png', wins: 19, podiums: 21 }, { name: 'Sergio Perez', points: 285, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SERPER01_Sergio_Perez/serper01.png.transform/2col/image.png', wins: 2, podiums: 9 }] },
      { id: 'mer', name: 'Mercedes', shortName: 'MER', color: '#00D2BE', points: 409, rank: 2, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2023/mercedes.png', drivers: [{ name: 'Lewis Hamilton', points: 234, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/2col/image.png', wins: 0, podiums: 6 }, { name: 'George Russell', points: 175, image: 'https://media.formula1.com/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png.transform/2col/image.png', wins: 0, podiums: 2 }] },
      { id: 'fer', name: 'Ferrari', shortName: 'FER', color: '#E80020', points: 406, rank: 3, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2023/ferrari.png', drivers: [{ name: 'Charles Leclerc', points: 206, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/2col/image.png', wins: 0, podiums: 6 }, { name: 'Carlos Sainz', points: 200, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png.transform/2col/image.png', wins: 1, podiums: 3 }] },
      { id: 'mcl', name: 'McLaren', shortName: 'MCL', color: '#FF8000', points: 302, rank: 4, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2023/mclaren.png', drivers: [{ name: 'Lando Norris', points: 205, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png.transform/2col/image.png', wins: 0, podiums: 7 }, { name: 'Oscar Piastri', points: 97, image: 'https://media.formula1.com/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png.transform/2col/image.png', wins: 0, podiums: 2 }] },
      { id: 'ast', name: 'Aston Martin', shortName: 'AMR', color: '#006F62', points: 280, rank: 5, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2023/aston-martin.png', drivers: [{ name: 'Fernando Alonso', points: 206, image: 'https://media.formula1.com/content/dam/fom-website/drivers/F/FERALO01_Fernando_Alonso/feralo01.png.transform/2col/image.png', wins: 0, podiums: 8 }, { name: 'Lance Stroll', points: 74, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'alp', name: 'Alpine', shortName: 'ALP', color: '#0090FF', points: 120, rank: 6, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2023/alpine.png', drivers: [{ name: 'Pierre Gasly', points: 62, image: 'https://media.formula1.com/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png.transform/2col/image.png', wins: 0, podiums: 1 }, { name: 'Esteban Ocon', points: 58, image: 'https://media.formula1.com/content/dam/fom-website/drivers/E/ESTOCO01_Esteban_Ocon/estoco01.png.transform/2col/image.png', wins: 0, podiums: 1 }] },
      { id: 'wil', name: 'Williams', shortName: 'WIL', color: '#005AFF', points: 28, rank: 7, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2023/williams.png', drivers: [{ name: 'Alex Albon', points: 27, image: 'https://media.formula1.com/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Logan Sargeant', points: 1, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LOGSAR01_Logan_Sargeant/logsar01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'at', name: 'AlphaTauri', shortName: 'AT', color: '#2B4562', points: 25, rank: 8, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2023/alphatauri.png', drivers: [{ name: 'Yuki Tsunoda', points: 17, image: 'https://media.formula1.com/content/dam/fom-website/drivers/Y/YUKTSU01_Yuki_Tsunoda/yuktsu01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Daniel Ricciardo', points: 6, image: 'https://media.formula1.com/content/dam/fom-website/drivers/D/DANRIC01_Daniel_Ricciardo/danric01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'alf', name: 'Alfa Romeo', shortName: 'ALF', color: '#900000', points: 16, rank: 9, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2023/alfa-romeo-racing.png', drivers: [{ name: 'Valtteri Bottas', points: 10, image: 'https://media.formula1.com/content/dam/fom-website/drivers/V/VALBOT01_Valtteri_Bottas/valbot01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Zhou Guanyu', points: 6, image: 'https://media.formula1.com/content/dam/fom-website/drivers/G/GUAZHO01_Zhou_Guanyu/guazho01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'haa', name: 'Haas', shortName: 'HAA', color: '#B6BABD', points: 12, rank: 10, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2023/haas-f1-team.png', drivers: [{ name: 'Nico Hulkenberg', points: 9, image: 'https://media.formula1.com/content/dam/fom-website/drivers/N/NICHUL01_Nico_Hulkenberg/nichul01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Kevin Magnussen', points: 3, image: 'https://media.formula1.com/content/dam/fom-website/drivers/K/KEVMAG01_Kevin_Magnussen/kevmag01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
    ],
  },
  2024: {
    title: 'THE MCLAREN RESURGENCE',
    rounds: '24 / 24',
    champion: 'Lando Norris',
    championTeam: 'McLaren',
    championColor: '#FF8000',
    teams: [
      { id: 'mcl', name: 'McLaren', shortName: 'MCL', color: '#FF8000', points: 666, rank: 1, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/mclaren.png', drivers: [{ name: 'Lando Norris', points: 340, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png.transform/2col/image.png', wins: 4, podiums: 14 }, { name: 'Oscar Piastri', points: 326, image: 'https://media.formula1.com/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png.transform/2col/image.png', wins: 3, podiums: 10 }] },
      { id: 'fer', name: 'Ferrari', shortName: 'FER', color: '#E80020', points: 630, rank: 2, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/ferrari.png', drivers: [{ name: 'Charles Leclerc', points: 325, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/2col/image.png', wins: 3, podiums: 11 }, { name: 'Carlos Sainz', points: 305, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png.transform/2col/image.png', wins: 2, podiums: 8 }] },
      { id: 'rbr', name: 'Red Bull Racing', shortName: 'RBR', color: '#0600EF', points: 590, rank: 3, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/red-bull-racing.png', drivers: [{ name: 'Max Verstappen', points: 415, image: 'https://media.formula1.com/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/2col/image.png', wins: 8, podiums: 15 }, { name: 'Sergio Perez', points: 175, image: 'https://media.formula1.com/content/dam/fom-website/drivers/S/SERPER01_Sergio_Perez/serper01.png.transform/2col/image.png', wins: 0, podiums: 4 }] },
      { id: 'mer', name: 'Mercedes', shortName: 'MER', color: '#00D2BE', points: 400, rank: 4, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/mercedes.png', drivers: [{ name: 'George Russell', points: 210, image: 'https://media.formula1.com/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png.transform/2col/image.png', wins: 1, podiums: 4 }, { name: 'Lewis Hamilton', points: 190, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/2col/image.png', wins: 2, podiums: 5 }] },
      { id: 'ast', name: 'Aston Martin', shortName: 'AMR', color: '#006F62', points: 95, rank: 5, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/aston-martin.png', drivers: [{ name: 'Fernando Alonso', points: 65, image: 'https://media.formula1.com/content/dam/fom-website/drivers/F/FERALO01_Fernando_Alonso/feralo01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Lance Stroll', points: 30, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'rb', name: 'VCARB', shortName: 'RB', color: '#1634CB', points: 45, rank: 6, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/rb.png', drivers: [{ name: 'Yuki Tsunoda', points: 30, image: 'https://media.formula1.com/content/dam/fom-website/drivers/Y/YUKTSU01_Yuki_Tsunoda/yuktsu01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Daniel Ricciardo', points: 15, image: 'https://media.formula1.com/content/dam/fom-website/drivers/D/DANRIC01_Daniel_Ricciardo/danric01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'haa', name: 'Haas', shortName: 'HAA', color: '#B6BABD', points: 40, rank: 7, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/haas-f1-team.png', drivers: [{ name: 'Nico Hulkenberg', points: 28, image: 'https://media.formula1.com/content/dam/fom-website/drivers/N/NICHUL01_Nico_Hulkenberg/nichul01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Kevin Magnussen', points: 12, image: 'https://media.formula1.com/content/dam/fom-website/drivers/K/KEVMAG01_Kevin_Magnussen/kevmag01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'wil', name: 'Williams', shortName: 'WIL', color: '#005AFF', points: 20, rank: 8, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/williams.png', drivers: [{ name: 'Alex Albon', points: 18, image: 'https://media.formula1.com/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Franco Colapinto', points: 2, image: 'https://media.formula1.com/content/dam/fom-website/drivers/F/FRACOL01_Franco_Colapinto/fracol01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'alp', name: 'Alpine', shortName: 'ALP', color: '#FF69B4', points: 18, rank: 9, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/alpine.png', drivers: [{ name: 'Pierre Gasly', points: 10, image: 'https://media.formula1.com/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Esteban Ocon', points: 8, image: 'https://media.formula1.com/content/dam/fom-website/drivers/E/ESTOCO01_Esteban_Ocon/estoco01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'sau', name: 'Kick Sauber', shortName: 'SAU', color: '#52E252', points: 0, rank: 10, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/kick-sauber.png', drivers: [{ name: 'Valtteri Bottas', points: 0, image: 'https://media.formula1.com/content/dam/fom-website/drivers/V/VALBOT01_Valtteri_Bottas/valbot01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Zhou Guanyu', points: 0, image: 'https://media.formula1.com/content/dam/fom-website/drivers/G/GUAZHO01_Zhou_Guanyu/guazho01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
    ],
  },
  2025: {
    title: 'THE NEW ERA',
    rounds: '24 / 24',
    champion: 'Lando Norris',
    championTeam: 'McLaren',
    championColor: '#FF8000',
    teams: [
      { id: 'mcl', name: 'McLaren', shortName: 'MCL', color: '#FF8000', points: 800, rank: 1, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/mclaren.png', drivers: [{ name: 'Lando Norris', points: 408, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png.transform/2col/image.png', wins: 7, podiums: 17 }, { name: 'Oscar Piastri', points: 392, image: 'https://media.formula1.com/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png.transform/2col/image.png', wins: 6, podiums: 15 }] },
      { id: 'fer', name: 'Ferrari', shortName: 'FER', color: '#E80020', points: 382, rank: 2, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/ferrari.png', drivers: [{ name: 'Charles Leclerc', points: 230, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/2col/image.png', wins: 2, podiums: 7 }, { name: 'Lewis Hamilton', points: 152, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/2col/image.png', wins: 1, podiums: 5 }] },
      { id: 'mer', name: 'Mercedes', shortName: 'MER', color: '#00D2BE', points: 459, rank: 3, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/mercedes.png', drivers: [{ name: 'George Russell', points: 309, image: 'https://media.formula1.com/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png.transform/2col/image.png', wins: 2, podiums: 9 }, { name: 'Kimi Antonelli', points: 150, image: 'https://media.formula1.com/content/dam/fom-website/drivers/K/KIMANT01_Kimi_Antonelli/kimant01.png.transform/2col/image.png', wins: 0, podiums: 3 }] },
      { id: 'rbr', name: 'Red Bull Racing', shortName: 'RBR', color: '#0600EF', points: 426, rank: 4, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/red-bull-racing.png', drivers: [{ name: 'Max Verstappen', points: 396, image: 'https://media.formula1.com/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/2col/image.png', wins: 7, podiums: 14 }, { name: 'Liam Lawson', points: 30, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LIALAW01_Liam_Lawson/lialaw01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'wil', name: 'Williams', shortName: 'WIL', color: '#005AFF', points: 137, rank: 5, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/williams.png', drivers: [{ name: 'Alex Albon', points: 73, image: 'https://media.formula1.com/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Carlos Sainz', points: 64, image: 'https://media.formula1.com/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png.transform/2col/image.png', wins: 0, podiums: 2 }] },
      { id: 'ast', name: 'Aston Martin', shortName: 'AMR', color: '#006F62', points: 85, rank: 6, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/aston-martin.png', drivers: [{ name: 'Fernando Alonso', points: 60, image: 'https://media.formula1.com/content/dam/fom-website/drivers/F/FERALO01_Fernando_Alonso/feralo01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Lance Stroll', points: 25, image: 'https://media.formula1.com/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'alp', name: 'Alpine', shortName: 'ALP', color: '#0090FF', points: 60, rank: 7, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/alpine.png', drivers: [{ name: 'Pierre Gasly', points: 40, image: 'https://media.formula1.com/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Jack Doohan', points: 20, image: 'https://media.formula1.com/content/dam/fom-website/drivers/J/JACDOO01_Jack_Doohan/jacdoo01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'haa', name: 'Haas', shortName: 'HAA', color: '#B6BABD', points: 45, rank: 8, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/haas-f1-team.png', drivers: [{ name: 'Esteban Ocon', points: 30, image: 'https://media.formula1.com/content/dam/fom-website/drivers/E/ESTOCO01_Esteban_Ocon/estoco01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Oliver Bearman', points: 15, image: 'https://media.formula1.com/content/dam/fom-website/drivers/O/OLIBEA01_Oliver_Bearman/olibea01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'rb', name: 'Racing Bulls', shortName: 'RB', color: '#1634CB', points: 40, rank: 9, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/rb.png', drivers: [{ name: 'Yuki Tsunoda', points: 30, image: 'https://media.formula1.com/content/dam/fom-website/drivers/Y/YUKTSU01_Yuki_Tsunoda/yuktsu01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Isack Hadjar', points: 10, image: 'https://media.formula1.com/content/dam/fom-website/drivers/I/ISAHAD01_Isack_Hadjar/isahad01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
      { id: 'sau', name: 'Kick Sauber', shortName: 'SAU', color: '#52E252', points: 15, rank: 10, carImage: 'https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/kick-sauber.png', drivers: [{ name: 'Nico Hulkenberg', points: 12, image: 'https://media.formula1.com/content/dam/fom-website/drivers/N/NICHUL01_Nico_Hulkenberg/nichul01.png.transform/2col/image.png', wins: 0, podiums: 0 }, { name: 'Gabriel Bortoleto', points: 3, image: 'https://media.formula1.com/content/dam/fom-website/drivers/G/GABBOr01_Gabriel_Bortoleto/gabbor01.png.transform/2col/image.png', wins: 0, podiums: 0 }] },
    ],
  },
};
const TEAMS: Team[] = [
  { id: 'redbull', name: 'Red Bull', fullTeamName: 'Oracle Red Bull Racing', points: 0, color: '#3671C6', base: 'Milton Keynes, UK', chief: 'Christian Horner', powerUnit: 'Honda RBPT', titles: 0, drivers: ['verstappen', 'perez'] },
  { id: 'mclaren', name: 'McLaren', fullTeamName: 'McLaren Formula 1 Team', points: 0, color: '#FF8000', base: 'Woking, UK', chief: 'Andrea Stella', powerUnit: 'Mercedes', titles: 0, drivers: ['norris', 'piastri'] },
  { id: 'ferrari', name: 'Ferrari', fullTeamName: 'Scuderia Ferrari HP', points: 0, color: '#E8002D', base: 'Maranello, Italy', chief: 'Fred Vasseur', powerUnit: 'Ferrari', titles: 0, drivers: ['leclerc', 'hamilton'] },
  { id: 'mercedes', name: 'Mercedes', fullTeamName: 'Mercedes-AMG PETRONAS F1 Team', points: 0, color: '#00D2BE', base: 'Brackley, UK', chief: 'Toto Wolff', powerUnit: 'Mercedes', titles: 0, drivers: ['russell', 'antonelli'] },
  { id: 'aston', name: 'Aston Martin', fullTeamName: 'Aston Martin Aramco F1 Team', points: 0, color: '#229971', base: 'Silverstone, UK', chief: 'Mike Krack', powerUnit: 'Mercedes', titles: 0, drivers: ['alonso', 'stroll'] },
  { id: 'alpine', name: 'Alpine', fullTeamName: 'BWT Alpine F1 Team', points: 0, color: '#FF87BC', base: 'Enstone, UK', chief: 'Oliver Oakes', powerUnit: 'Renault', titles: 0, drivers: ['gasly', 'doohan'] },
  { id: 'williams', name: 'Williams', fullTeamName: 'Williams Racing', points: 0, color: '#64C4FF', base: 'Grove, UK', chief: 'James Vowles', powerUnit: 'Mercedes', titles: 0, drivers: ['albon', 'sargeant'] },
  { id: 'rb', name: 'VCARB', fullTeamName: 'Visa Cash App RB F1 Team', points: 0, color: '#6692FF', base: 'Faenza, Italy', chief: 'Laurent Mekies', powerUnit: 'Honda RBPT', titles: 0, drivers: ['tsunoda', 'ricciardo'] },
  { id: 'haas', name: 'Haas', fullTeamName: 'MoneyGram Haas F1 Team', points: 0, color: '#B6BABD', base: 'Kannapolis, USA', chief: 'Ayao Komatsu', powerUnit: 'Ferrari', titles: 0, drivers: ['hulkenberg', 'magnussen'] },
  { id: 'sauber', name: 'Kick Sauber', fullTeamName: 'Stake F1 Team Kick Sauber', points: 0, color: '#52E252', base: 'Hinwil, Switzerland', chief: 'Mattia Binotto', powerUnit: 'Ferrari', titles: 0, drivers: ['hulkenberg', 'zhou'] },
  { id: 'audi', name: 'Audi F1', fullTeamName: 'Audi Formula 1 Team', points: 0, color: '#F2F2F2', base: 'Neuburg, Germany', chief: 'Jonathan Wheatley', powerUnit: 'Audi', titles: 0, drivers: [], isFuture: true },
  { id: 'cadillac', name: 'Cadillac', fullTeamName: 'Cadillac F1 Team', points: 0, color: '#D4AF37', base: 'Fishers, USA', chief: 'Michael Andretti', powerUnit: 'GM/Cadillac', titles: 0, drivers: [], isFuture: true },
];

const RACES_2018: Race[] = [
  { round: 1, name: 'Bahrain Grand Prix', circuit: 'Sakhir', date: 'Mar 25', image: TRACK_IMAGES['bahrain-grand-prix'] || MonacoGpImage, laps: 57, length: 'Sakhir', trackId: 'bahrain-grand-prix', rainProb: 0, grandPrixSlug: 'bahrain-grand-prix' },
  { round: 2, name: 'China Grand Prix', circuit: 'Shanghai', date: 'Apr 15', image: TRACK_IMAGES['chinese-grand-prix'] || MonacoGpImage, laps: 56, length: 'Shanghai', trackId: 'chinese-grand-prix', rainProb: 0, grandPrixSlug: 'chinese-grand-prix' },
  { round: 3, name: 'Russia Grand Prix', circuit: 'Sochi', date: 'Apr 29', image: TRACK_IMAGES['russian-grand-prix'] || MonacoGpImage, laps: 53, length: 'Sochi', trackId: 'russian-grand-prix', rainProb: 0, grandPrixSlug: 'russian-grand-prix' },
  { round: 4, name: 'Azerbaijan Grand Prix', circuit: 'Baku', date: 'Apr 29', image: TRACK_IMAGES['azerbaijan-grand-prix'] || MonacoGpImage, laps: 51, length: 'Baku', trackId: 'azerbaijan-grand-prix', rainProb: 0, grandPrixSlug: 'azerbaijan-grand-prix' },
  { round: 5, name: 'Spain Grand Prix', circuit: 'Barcelona', date: 'May 13', image: TRACK_IMAGES['spanish-grand-prix'] || MonacoGpImage, laps: 66, length: 'Barcelona', trackId: 'spanish-grand-prix', rainProb: 0, grandPrixSlug: 'spanish-grand-prix' },
  { round: 6, name: 'Monaco Grand Prix', circuit: 'Monte Carlo', date: 'May 27', image: TRACK_IMAGES['monaco-grand-prix'] || MonacoGpImage, laps: 78, length: 'Monte Carlo', trackId: 'monaco-grand-prix', rainProb: 0, grandPrixSlug: 'monaco-grand-prix' },
  { round: 7, name: 'Canada Grand Prix', circuit: 'Montreal', date: 'Jun 10', image: TRACK_IMAGES['canadian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Montreal', trackId: 'canadian-grand-prix', rainProb: 0, grandPrixSlug: 'canadian-grand-prix' },
  { round: 8, name: 'France Grand Prix', circuit: 'Paul Ricard', date: 'Jun 24', image: TRACK_IMAGES['french-grand-prix'] || MonacoGpImage, laps: 71, length: 'Paul Ricard', trackId: 'french-grand-prix', rainProb: 0, grandPrixSlug: 'french-grand-prix' },
  { round: 9, name: 'Austria Grand Prix', circuit: 'Spielberg', date: 'Jul 1', image: TRACK_IMAGES['austrian-grand-prix'] || MonacoGpImage, laps: 71, length: 'Spielberg', trackId: 'austrian-grand-prix', rainProb: 0, grandPrixSlug: 'austrian-grand-prix' },
  { round: 10, name: 'Great Britain Grand Prix', circuit: 'Silverstone', date: 'Jul 8', image: TRACK_IMAGES['british-grand-prix'] || MonacoGpImage, laps: 52, length: 'Silverstone', trackId: 'british-grand-prix', rainProb: 0, grandPrixSlug: 'british-grand-prix' },
  { round: 11, name: 'Germany Grand Prix', circuit: 'Hockenheim', date: 'Jul 22', image: TRACK_IMAGES['german-grand-prix'] || MonacoGpImage, laps: 67, length: 'Hockenheim', trackId: 'german-grand-prix', rainProb: 0, grandPrixSlug: 'german-grand-prix' },
  { round: 12, name: 'Hungary Grand Prix', circuit: 'Budapest', date: 'Aug 5', image: TRACK_IMAGES['hungarian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Budapest', trackId: 'hungarian-grand-prix', rainProb: 0, grandPrixSlug: 'hungarian-grand-prix' },
  { round: 13, name: 'Belgium Grand Prix', circuit: 'Spa', date: 'Aug 26', image: TRACK_IMAGES['belgian-grand-prix'] || MonacoGpImage, laps: 44, length: 'Spa', trackId: 'belgian-grand-prix', rainProb: 0, grandPrixSlug: 'belgian-grand-prix' },
  { round: 14, name: 'Italy Grand Prix', circuit: 'Monza', date: 'Sep 2', image: TRACK_IMAGES['italian-grand-prix'] || MonacoGpImage, laps: 53, length: 'Monza', trackId: 'italian-grand-prix', rainProb: 0, grandPrixSlug: 'italian-grand-prix' },
  { round: 15, name: 'Singapore Grand Prix', circuit: 'Marina Bay', date: 'Sep 16', image: TRACK_IMAGES['singapore-grand-prix'] || MonacoGpImage, laps: 61, length: 'Marina Bay', trackId: 'singapore-grand-prix', rainProb: 0, grandPrixSlug: 'singapore-grand-prix' },
  { round: 16, name: 'Japan Grand Prix', circuit: 'Suzuka', date: 'Oct 7', image: TRACK_IMAGES['japanese-grand-prix'] || MonacoGpImage, laps: 53, length: 'Suzuka', trackId: 'japanese-grand-prix', rainProb: 0, grandPrixSlug: 'japanese-grand-prix' },
  { round: 17, name: 'Russia Grand Prix', circuit: 'Sochi', date: 'Sep 30', image: TRACK_IMAGES['russian-grand-prix'] || MonacoGpImage, laps: 53, length: 'Sochi', trackId: 'russian-grand-prix', rainProb: 0, grandPrixSlug: 'russian-grand-prix' },
  { round: 18, name: 'United States Grand Prix', circuit: 'Austin', date: 'Oct 21', image: TRACK_IMAGES['united-states-grand-prix'] || MonacoGpImage, laps: 56, length: 'Austin', trackId: 'united-states-grand-prix', rainProb: 0, grandPrixSlug: 'united-states-grand-prix' },
  { round: 19, name: 'Mexico Grand Prix', circuit: 'Mexico City', date: 'Oct 28', image: TRACK_IMAGES['mexican-grand-prix'] || MonacoGpImage, laps: 71, length: 'Mexico City', trackId: 'mexican-grand-prix', rainProb: 0, grandPrixSlug: 'mexican-grand-prix' },
  { round: 20, name: 'Brazil Grand Prix', circuit: 'Interlagos', date: 'Nov 11', image: TRACK_IMAGES['brazilian-grand-prix'] || MonacoGpImage, laps: 71, length: 'Interlagos', trackId: 'brazilian-grand-prix', rainProb: 0, grandPrixSlug: 'brazilian-grand-prix' },
  { round: 21, name: 'Abu Dhabi Grand Prix', circuit: 'Yas Island', date: 'Nov 25', image: TRACK_IMAGES['abu-dhabi-grand-prix'] || MonacoGpImage, laps: 55, length: 'Yas Island', trackId: 'abu-dhabi-grand-prix', rainProb: 0, grandPrixSlug: 'abu-dhabi-grand-prix' },
];

const RACES_2019: Race[] = [
  { round: 1, name: 'Bahrain Grand Prix', circuit: 'Sakhir', date: 'Mar 31', image: TRACK_IMAGES['bahrain-grand-prix'] || MonacoGpImage, laps: 57, length: 'Sakhir', trackId: 'bahrain-grand-prix', rainProb: 0, grandPrixSlug: 'bahrain-grand-prix' },
  { round: 2, name: 'China Grand Prix', circuit: 'Shanghai', date: 'Apr 14', image: TRACK_IMAGES['chinese-grand-prix'] || MonacoGpImage, laps: 56, length: 'Shanghai', trackId: 'chinese-grand-prix', rainProb: 0, grandPrixSlug: 'chinese-grand-prix' },
  { round: 3, name: 'Vietnam Grand Prix', circuit: 'Hanoi', date: 'Apr 14', image: TRACK_IMAGES['vietnamese-grand-prix'] || MonacoGpImage, laps: 56, length: 'Hanoi', trackId: 'vietnamese-grand-prix', rainProb: 0, grandPrixSlug: 'vietnamese-grand-prix' },
  { round: 4, name: 'Azerbaijan Grand Prix', circuit: 'Baku', date: 'Apr 28', image: TRACK_IMAGES['azerbaijan-grand-prix'] || MonacoGpImage, laps: 51, length: 'Baku', trackId: 'azerbaijan-grand-prix', rainProb: 0, grandPrixSlug: 'azerbaijan-grand-prix' },
  { round: 5, name: 'Spain Grand Prix', circuit: 'Barcelona', date: 'May 12', image: TRACK_IMAGES['spanish-grand-prix'] || MonacoGpImage, laps: 66, length: 'Barcelona', trackId: 'spanish-grand-prix', rainProb: 0, grandPrixSlug: 'spanish-grand-prix' },
  { round: 6, name: 'Monaco Grand Prix', circuit: 'Monte Carlo', date: 'May 26', image: TRACK_IMAGES['monaco-grand-prix'] || MonacoGpImage, laps: 78, length: 'Monte Carlo', trackId: 'monaco-grand-prix', rainProb: 0, grandPrixSlug: 'monaco-grand-prix' },
  { round: 7, name: 'Canada Grand Prix', circuit: 'Montreal', date: 'Jun 9', image: TRACK_IMAGES['canadian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Montreal', trackId: 'canadian-grand-prix', rainProb: 0, grandPrixSlug: 'canadian-grand-prix' },
  { round: 8, name: 'France Grand Prix', circuit: 'Paul Ricard', date: 'Jun 23', image: TRACK_IMAGES['french-grand-prix'] || MonacoGpImage, laps: 53, length: 'Paul Ricard', trackId: 'french-grand-prix', rainProb: 0, grandPrixSlug: 'french-grand-prix' },
  { round: 9, name: 'Austria Grand Prix', circuit: 'Spielberg', date: 'Jun 30', image: TRACK_IMAGES['austrian-grand-prix'] || MonacoGpImage, laps: 71, length: 'Spielberg', trackId: 'austrian-grand-prix', rainProb: 0, grandPrixSlug: 'austrian-grand-prix' },
  { round: 10, name: 'Great Britain Grand Prix', circuit: 'Silverstone', date: 'Jul 14', image: TRACK_IMAGES['british-grand-prix'] || MonacoGpImage, laps: 52, length: 'Silverstone', trackId: 'british-grand-prix', rainProb: 0, grandPrixSlug: 'british-grand-prix' },
  { round: 11, name: 'Germany Grand Prix', circuit: 'Hockenheim', date: 'Jul 28', image: TRACK_IMAGES['german-grand-prix'] || MonacoGpImage, laps: 67, length: 'Hockenheim', trackId: 'german-grand-prix', rainProb: 0, grandPrixSlug: 'german-grand-prix' },
  { round: 12, name: 'Hungary Grand Prix', circuit: 'Budapest', date: 'Aug 4', image: TRACK_IMAGES['hungarian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Budapest', trackId: 'hungarian-grand-prix', rainProb: 0, grandPrixSlug: 'hungarian-grand-prix' },
  { round: 13, name: 'Belgium Grand Prix', circuit: 'Spa', date: 'Aug 25', image: TRACK_IMAGES['belgian-grand-prix'] || MonacoGpImage, laps: 44, length: 'Spa', trackId: 'belgian-grand-prix', rainProb: 0, grandPrixSlug: 'belgian-grand-prix' },
  { round: 14, name: 'Italy Grand Prix', circuit: 'Monza', date: 'Sep 1', image: TRACK_IMAGES['italian-grand-prix'] || MonacoGpImage, laps: 53, length: 'Monza', trackId: 'italian-grand-prix', rainProb: 0, grandPrixSlug: 'italian-grand-prix' },
  { round: 15, name: 'Singapore Grand Prix', circuit: 'Marina Bay', date: 'Sep 22', image: TRACK_IMAGES['singapore-grand-prix'] || MonacoGpImage, laps: 61, length: 'Marina Bay', trackId: 'singapore-grand-prix', rainProb: 0, grandPrixSlug: 'singapore-grand-prix' },
  { round: 16, name: 'Japan Grand Prix', circuit: 'Suzuka', date: 'Oct 13', image: TRACK_IMAGES['japanese-grand-prix'] || MonacoGpImage, laps: 53, length: 'Suzuka', trackId: 'japanese-grand-prix', rainProb: 0, grandPrixSlug: 'japanese-grand-prix' },
  { round: 17, name: 'Mexico Grand Prix', circuit: 'Mexico City', date: 'Oct 27', image: TRACK_IMAGES['mexican-grand-prix'] || MonacoGpImage, laps: 71, length: 'Mexico City', trackId: 'mexican-grand-prix', rainProb: 0, grandPrixSlug: 'mexican-grand-prix' },
  { round: 18, name: 'United States Grand Prix', circuit: 'Austin', date: 'Nov 3', image: TRACK_IMAGES['united-states-grand-prix'] || MonacoGpImage, laps: 56, length: 'Austin', trackId: 'united-states-grand-prix', rainProb: 0, grandPrixSlug: 'united-states-grand-prix' },
  { round: 19, name: 'Brazil Grand Prix', circuit: 'Interlagos', date: 'Nov 17', image: TRACK_IMAGES['brazilian-grand-prix'] || MonacoGpImage, laps: 71, length: 'Interlagos', trackId: 'brazilian-grand-prix', rainProb: 0, grandPrixSlug: 'brazilian-grand-prix' },
  { round: 20, name: 'Abu Dhabi Grand Prix', circuit: 'Yas Island', date: 'Dec 1', image: TRACK_IMAGES['abu-dhabi-grand-prix'] || MonacoGpImage, laps: 55, length: 'Yas Island', trackId: 'abu-dhabi-grand-prix', rainProb: 0, grandPrixSlug: 'abu-dhabi-grand-prix' },
];

const RACES_2020: Race[] = [
  { round: 1, name: 'Austria Grand Prix', circuit: 'Spielberg', date: 'Jul 5', image: TRACK_IMAGES['austrian-grand-prix'] || MonacoGpImage, laps: 71, length: 'Spielberg', trackId: 'austrian-grand-prix', rainProb: 0, grandPrixSlug: 'austrian-grand-prix' },
  { round: 2, name: 'Styria Grand Prix', circuit: 'Spielberg', date: 'Jul 12', image: TRACK_IMAGES['styrian-grand-prix'] || MonacoGpImage, laps: 71, length: 'Spielberg', trackId: 'styrian-grand-prix', rainProb: 0, grandPrixSlug: 'styrian-grand-prix' },
  { round: 3, name: 'Hungary Grand Prix', circuit: 'Budapest', date: 'Jul 19', image: TRACK_IMAGES['hungarian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Budapest', trackId: 'hungarian-grand-prix', rainProb: 0, grandPrixSlug: 'hungarian-grand-prix' },
  { round: 4, name: 'Great Britain Grand Prix', circuit: 'Silverstone', date: 'Aug 2', image: TRACK_IMAGES['british-grand-prix'] || MonacoGpImage, laps: 52, length: 'Silverstone', trackId: 'british-grand-prix', rainProb: 0, grandPrixSlug: 'british-grand-prix' },
];

const RACES_2021: Race[] = [
  { round: 1, name: 'Bahrain Grand Prix', circuit: 'Sakhir', date: 'Mar 28', image: TRACK_IMAGES['bahrain-grand-prix'] || MonacoGpImage, laps: 57, length: 'Sakhir', trackId: 'bahrain-grand-prix', rainProb: 0, grandPrixSlug: 'bahrain-grand-prix' },
  { round: 2, name: 'Emilia Romagna Grand Prix', circuit: 'Imola', date: 'Apr 18', image: TRACK_IMAGES['emilia-romagna-grand-prix'] || MonacoGpImage, laps: 63, length: 'Imola', trackId: 'emilia-romagna-grand-prix', rainProb: 0, grandPrixSlug: 'emilia-romagna-grand-prix' },
  { round: 3, name: 'Portugal Grand Prix', circuit: 'Portimao', date: 'May 2', image: TRACK_IMAGES['portuguese-grand-prix'] || MonacoGpImage, laps: 66, length: 'Portimao', trackId: 'portuguese-grand-prix', rainProb: 0, grandPrixSlug: 'portuguese-grand-prix' },
  { round: 4, name: 'Spain Grand Prix', circuit: 'Barcelona', date: 'May 9', image: TRACK_IMAGES['spanish-grand-prix'] || MonacoGpImage, laps: 66, length: 'Barcelona', trackId: 'spanish-grand-prix', rainProb: 0, grandPrixSlug: 'spanish-grand-prix' },
  { round: 5, name: 'Monaco Grand Prix', circuit: 'Monte Carlo', date: 'May 23', image: TRACK_IMAGES['monaco-grand-prix'] || MonacoGpImage, laps: 78, length: 'Monte Carlo', trackId: 'monaco-grand-prix', rainProb: 0, grandPrixSlug: 'monaco-grand-prix' },
  { round: 6, name: 'Azerbaijan Grand Prix', circuit: 'Baku', date: 'Jun 6', image: TRACK_IMAGES['azerbaijan-grand-prix'] || MonacoGpImage, laps: 51, length: 'Baku', trackId: 'azerbaijan-grand-prix', rainProb: 0, grandPrixSlug: 'azerbaijan-grand-prix' },
  { round: 7, name: 'France Grand Prix', circuit: 'Paul Ricard', date: 'Jun 20', image: TRACK_IMAGES['french-grand-prix'] || MonacoGpImage, laps: 53, length: 'Paul Ricard', trackId: 'french-grand-prix', rainProb: 0, grandPrixSlug: 'french-grand-prix' },
  { round: 8, name: 'Styria Grand Prix', circuit: 'Spielberg', date: 'Jul 4', image: TRACK_IMAGES['styrian-grand-prix'] || MonacoGpImage, laps: 71, length: 'Spielberg', trackId: 'styrian-grand-prix', rainProb: 0, grandPrixSlug: 'styrian-grand-prix' },
  { round: 9, name: 'Austria Grand Prix', circuit: 'Spielberg', date: 'Jul 11', image: TRACK_IMAGES['austrian-grand-prix'] || MonacoGpImage, laps: 71, length: 'Spielberg', trackId: 'austrian-grand-prix', rainProb: 0, grandPrixSlug: 'austrian-grand-prix' },
  { round: 10, name: 'Great Britain Grand Prix', circuit: 'Silverstone', date: 'Jul 18', image: TRACK_IMAGES['british-grand-prix'] || MonacoGpImage, laps: 52, length: 'Silverstone', trackId: 'british-grand-prix', rainProb: 0, grandPrixSlug: 'british-grand-prix' },
  { round: 11, name: 'Hungary Grand Prix', circuit: 'Budapest', date: 'Aug 1', image: TRACK_IMAGES['hungarian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Budapest', trackId: 'hungarian-grand-prix', rainProb: 0, grandPrixSlug: 'hungarian-grand-prix' },
  { round: 12, name: 'Belgium Grand Prix', circuit: 'Spa', date: 'Aug 29', image: TRACK_IMAGES['belgian-grand-prix'] || MonacoGpImage, laps: 44, length: 'Spa', trackId: 'belgian-grand-prix', rainProb: 0, grandPrixSlug: 'belgian-grand-prix' },
  { round: 13, name: 'Netherlands Grand Prix', circuit: 'Zandvoort', date: 'Sep 5', image: TRACK_IMAGES['dutch-grand-prix'] || MonacoGpImage, laps: 72, length: 'Zandvoort', trackId: 'dutch-grand-prix', rainProb: 0, grandPrixSlug: 'dutch-grand-prix' },
  { round: 14, name: 'Italy Grand Prix', circuit: 'Monza', date: 'Sep 12', image: TRACK_IMAGES['italian-grand-prix'] || MonacoGpImage, laps: 53, length: 'Monza', trackId: 'italian-grand-prix', rainProb: 0, grandPrixSlug: 'italian-grand-prix' },
  { round: 15, name: 'Russia Grand Prix', circuit: 'Sochi', date: 'Sep 26', image: TRACK_IMAGES['russian-grand-prix'] || MonacoGpImage, laps: 53, length: 'Sochi', trackId: 'russian-grand-prix', rainProb: 0, grandPrixSlug: 'russian-grand-prix' },
  { round: 16, name: 'Turkey Grand Prix', circuit: 'Istanbul', date: 'Oct 10', image: TRACK_IMAGES['turkish-grand-prix'] || MonacoGpImage, laps: 58, length: 'Istanbul', trackId: 'turkish-grand-prix', rainProb: 0, grandPrixSlug: 'turkish-grand-prix' },
  { round: 17, name: 'United States Grand Prix', circuit: 'Austin', date: 'Oct 24', image: TRACK_IMAGES['united-states-grand-prix'] || MonacoGpImage, laps: 56, length: 'Austin', trackId: 'united-states-grand-prix', rainProb: 0, grandPrixSlug: 'united-states-grand-prix' },
  { round: 18, name: 'Mexico Grand Prix', circuit: 'Mexico City', date: 'Nov 7', image: TRACK_IMAGES['mexico-city-grand-prix'] || MonacoGpImage, laps: 71, length: 'Mexico City', trackId: 'mexico-city-grand-prix', rainProb: 0, grandPrixSlug: 'mexico-city-grand-prix' },
  { round: 19, name: 'Brazil Grand Prix', circuit: 'Interlagos', date: 'Nov 14', image: TRACK_IMAGES['s-o-paulo-grand-prix'] || MonacoGpImage, laps: 71, length: 'Interlagos', trackId: 's-o-paulo-grand-prix', rainProb: 0, grandPrixSlug: 's-o-paulo-grand-prix' },
  { round: 20, name: 'Saudi Arabia Grand Prix', circuit: 'Jeddah', date: 'Dec 5', image: TRACK_IMAGES['saudi-arabian-grand-prix'] || MonacoGpImage, laps: 50, length: 'Jeddah', trackId: 'saudi-arabian-grand-prix', rainProb: 0, grandPrixSlug: 'saudi-arabian-grand-prix' },
  { round: 21, name: 'Abu Dhabi Grand Prix', circuit: 'Yas Island', date: 'Dec 12', image: TRACK_IMAGES['abu-dhabi-grand-prix'] || MonacoGpImage, laps: 55, length: 'Yas Island', trackId: 'abu-dhabi-grand-prix', rainProb: 0, grandPrixSlug: 'abu-dhabi-grand-prix' },
  { round: 22, name: 'Qatar Grand Prix', circuit: 'Lusail', date: 'Nov 21', image: TRACK_IMAGES['qatar-grand-prix'] || MonacoGpImage, laps: 57, length: 'Lusail', trackId: 'qatar-grand-prix', rainProb: 0, grandPrixSlug: 'qatar-grand-prix' },
];

const RACES_2022: Race[] = [
  { round: 1, name: 'Bahrain Grand Prix', circuit: 'Sakhir', date: 'Mar 20', image: TRACK_IMAGES['bahrain-grand-prix'] || MonacoGpImage, laps: 57, length: 'Sakhir', trackId: 'bahrain-grand-prix', rainProb: 0, grandPrixSlug: 'bahrain-grand-prix' },
  { round: 2, name: 'Saudi Arabia Grand Prix', circuit: 'Jeddah', date: 'Mar 27', image: TRACK_IMAGES['saudi-arabian-grand-prix'] || MonacoGpImage, laps: 50, length: 'Jeddah', trackId: 'saudi-arabian-grand-prix', rainProb: 0, grandPrixSlug: 'saudi-arabian-grand-prix' },
  { round: 3, name: 'Australia Grand Prix', circuit: 'Melbourne', date: 'Apr 10', image: TRACK_IMAGES['australian-grand-prix'] || MonacoGpImage, laps: 58, length: 'Melbourne', trackId: 'australian-grand-prix', rainProb: 0, grandPrixSlug: 'australian-grand-prix' },
  { round: 4, name: 'Emilia Romagna Grand Prix', circuit: 'Imola', date: 'Apr 24', image: TRACK_IMAGES['emilia-romagna-grand-prix'] || MonacoGpImage, laps: 63, length: 'Imola', trackId: 'emilia-romagna-grand-prix', rainProb: 0, grandPrixSlug: 'emilia-romagna-grand-prix' },
  { round: 5, name: 'Miami Grand Prix', circuit: 'Miami', date: 'May 8', image: TRACK_IMAGES['miami-grand-prix'] || MonacoGpImage, laps: 57, length: 'Miami', trackId: 'miami-grand-prix', rainProb: 0, grandPrixSlug: 'miami-grand-prix' },
  { round: 6, name: 'Spain Grand Prix', circuit: 'Barcelona', date: 'May 22', image: TRACK_IMAGES['spanish-grand-prix'] || MonacoGpImage, laps: 66, length: 'Barcelona', trackId: 'spanish-grand-prix', rainProb: 0, grandPrixSlug: 'spanish-grand-prix' },
  { round: 7, name: 'Monaco Grand Prix', circuit: 'Monte Carlo', date: 'May 29', image: TRACK_IMAGES['monaco-grand-prix'] || MonacoGpImage, laps: 78, length: 'Monte Carlo', trackId: 'monaco-grand-prix', rainProb: 0, grandPrixSlug: 'monaco-grand-prix' },
  { round: 8, name: 'Azerbaijan Grand Prix', circuit: 'Baku', date: 'Jun 12', image: TRACK_IMAGES['azerbaijan-grand-prix'] || MonacoGpImage, laps: 51, length: 'Baku', trackId: 'azerbaijan-grand-prix', rainProb: 0, grandPrixSlug: 'azerbaijan-grand-prix' },
  { round: 9, name: 'Canada Grand Prix', circuit: 'Montreal', date: 'Jun 19', image: TRACK_IMAGES['canadian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Montreal', trackId: 'canadian-grand-prix', rainProb: 0, grandPrixSlug: 'canadian-grand-prix' },
];

const RACES_2023: Race[] = [
  { round: 1, name: 'Bahrain Grand Prix', circuit: 'Sakhir', date: 'Mar 5', image: TRACK_IMAGES['bahrain-grand-prix'] || MonacoGpImage, laps: 57, length: 'Sakhir', trackId: 'bahrain-grand-prix', rainProb: 0, grandPrixSlug: 'bahrain-grand-prix' },
  { round: 2, name: 'Saudi Arabia Grand Prix', circuit: 'Jeddah', date: 'Mar 19', image: TRACK_IMAGES['saudi-arabian-grand-prix'] || MonacoGpImage, laps: 50, length: 'Jeddah', trackId: 'saudi-arabian-grand-prix', rainProb: 0, grandPrixSlug: 'saudi-arabian-grand-prix' },
  { round: 3, name: 'Australia Grand Prix', circuit: 'Melbourne', date: 'Apr 2', image: TRACK_IMAGES['australian-grand-prix'] || MonacoGpImage, laps: 58, length: 'Melbourne', trackId: 'australian-grand-prix', rainProb: 0, grandPrixSlug: 'australian-grand-prix' },
  { round: 4, name: 'Azerbaijan Grand Prix', circuit: 'Baku', date: 'Apr 30', image: TRACK_IMAGES['azerbaijan-grand-prix'] || MonacoGpImage, laps: 51, length: 'Baku', trackId: 'azerbaijan-grand-prix', rainProb: 0, grandPrixSlug: 'azerbaijan-grand-prix' },
  { round: 5, name: 'Miami Grand Prix', circuit: 'Miami', date: 'May 7', image: TRACK_IMAGES['miami-grand-prix'] || MonacoGpImage, laps: 57, length: 'Miami', trackId: 'miami-grand-prix', rainProb: 0, grandPrixSlug: 'miami-grand-prix' },
  { round: 6, name: 'Monaco Grand Prix', circuit: 'Monte Carlo', date: 'May 28', image: TRACK_IMAGES['monaco-grand-prix'] || MonacoGpImage, laps: 78, length: 'Monte Carlo', trackId: 'monaco-grand-prix', rainProb: 0, grandPrixSlug: 'monaco-grand-prix' },
  { round: 7, name: 'Spain Grand Prix', circuit: 'Barcelona', date: 'Jun 4', image: TRACK_IMAGES['spanish-grand-prix'] || MonacoGpImage, laps: 66, length: 'Barcelona', trackId: 'spanish-grand-prix', rainProb: 0, grandPrixSlug: 'spanish-grand-prix' },
  { round: 8, name: 'Canada Grand Prix', circuit: 'Montreal', date: 'Jun 18', image: TRACK_IMAGES['canadian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Montreal', trackId: 'canadian-grand-prix', rainProb: 0, grandPrixSlug: 'canadian-grand-prix' },
  { round: 9, name: 'Austria Grand Prix', circuit: 'Spielberg', date: 'Jul 2', image: TRACK_IMAGES['austrian-grand-prix'] || MonacoGpImage, laps: 71, length: 'Spielberg', trackId: 'austrian-grand-prix', rainProb: 0, grandPrixSlug: 'austrian-grand-prix' },
  { round: 10, name: 'Great Britain Grand Prix', circuit: 'Silverstone', date: 'Jul 9', image: TRACK_IMAGES['british-grand-prix'] || MonacoGpImage, laps: 52, length: 'Silverstone', trackId: 'british-grand-prix', rainProb: 0, grandPrixSlug: 'british-grand-prix' },
  { round: 11, name: 'Hungary Grand Prix', circuit: 'Budapest', date: 'Jul 23', image: TRACK_IMAGES['hungarian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Budapest', trackId: 'hungarian-grand-prix', rainProb: 0, grandPrixSlug: 'hungarian-grand-prix' },
  { round: 12, name: 'Belgium Grand Prix', circuit: 'Spa', date: 'Jul 30', image: TRACK_IMAGES['belgian-grand-prix'] || MonacoGpImage, laps: 44, length: 'Spa', trackId: 'belgian-grand-prix', rainProb: 0, grandPrixSlug: 'belgian-grand-prix' },
  { round: 13, name: 'Netherlands Grand Prix', circuit: 'Zandvoort', date: 'Aug 27', image: TRACK_IMAGES['dutch-grand-prix'] || MonacoGpImage, laps: 72, length: 'Zandvoort', trackId: 'dutch-grand-prix', rainProb: 0, grandPrixSlug: 'dutch-grand-prix' },
  { round: 14, name: 'Italy Grand Prix', circuit: 'Monza', date: 'Sep 3', image: TRACK_IMAGES['italian-grand-prix'] || MonacoGpImage, laps: 53, length: 'Monza', trackId: 'italian-grand-prix', rainProb: 0, grandPrixSlug: 'italian-grand-prix' },
  { round: 15, name: 'Singapore Grand Prix', circuit: 'Marina Bay', date: 'Sep 17', image: TRACK_IMAGES['singapore-grand-prix'] || MonacoGpImage, laps: 61, length: 'Marina Bay', trackId: 'singapore-grand-prix', rainProb: 0, grandPrixSlug: 'singapore-grand-prix' },
  { round: 16, name: 'Japan Grand Prix', circuit: 'Suzuka', date: 'Oct 8', image: TRACK_IMAGES['japanese-grand-prix'] || MonacoGpImage, laps: 53, length: 'Suzuka', trackId: 'japanese-grand-prix', rainProb: 0, grandPrixSlug: 'japanese-grand-prix' },
  { round: 17, name: 'Qatar Grand Prix', circuit: 'Lusail', date: 'Oct 8', image: TRACK_IMAGES['qatar-grand-prix'] || MonacoGpImage, laps: 57, length: 'Lusail', trackId: 'qatar-grand-prix', rainProb: 0, grandPrixSlug: 'qatar-grand-prix' },
  { round: 18, name: 'United States Grand Prix', circuit: 'Austin', date: 'Oct 22', image: TRACK_IMAGES['united-states-grand-prix'] || MonacoGpImage, laps: 56, length: 'Austin', trackId: 'united-states-grand-prix', rainProb: 0, grandPrixSlug: 'united-states-grand-prix' },
  { round: 19, name: 'Mexico Grand Prix', circuit: 'Mexico City', date: 'Oct 29', image: TRACK_IMAGES['mexico-city-grand-prix'] || MonacoGpImage, laps: 71, length: 'Mexico City', trackId: 'mexico-city-grand-prix', rainProb: 0, grandPrixSlug: 'mexico-city-grand-prix' },
  { round: 20, name: 'Brazil Grand Prix', circuit: 'Interlagos', date: 'Nov 5', image: TRACK_IMAGES['sao-paulo-grand-prix'] || MonacoGpImage, laps: 71, length: 'Interlagos', trackId: 'sao-paulo-grand-prix', rainProb: 0, grandPrixSlug: 'sao-paulo-grand-prix' },
  { round: 21, name: 'Las Vegas Grand Prix', circuit: 'Las Vegas', date: 'Nov 18', image: TRACK_IMAGES['las-vegas-grand-prix'] || MonacoGpImage, laps: 62, length: 'Las Vegas', trackId: 'las-vegas-grand-prix', rainProb: 0, grandPrixSlug: 'las-vegas-grand-prix' },
  { round: 22, name: 'Abu Dhabi Grand Prix', circuit: 'Yas Island', date: 'Dec 8', image: TRACK_IMAGES['abu-dhabi-grand-prix'] || MonacoGpImage, laps: 55, length: 'Yas Island', trackId: 'abu-dhabi-grand-prix', rainProb: 0, grandPrixSlug: 'abu-dhabi-grand-prix' },
];

const RACES_2024: Race[] = [
  { round: 1, name: 'Bahrain Grand Prix', circuit: 'Sakhir', date: 'Mar 2', image: TRACK_IMAGES['bahrain-grand-prix'] || MonacoGpImage, laps: 57, length: 'Sakhir', trackId: 'bahrain-grand-prix', rainProb: 0, grandPrixSlug: 'bahrain-grand-prix' },
  { round: 2, name: 'Saudi Arabia Grand Prix', circuit: 'Jeddah', date: 'Mar 9', image: TRACK_IMAGES['saudi-arabian-grand-prix'] || MonacoGpImage, laps: 50, length: 'Jeddah', trackId: 'saudi-arabian-grand-prix', rainProb: 0, grandPrixSlug: 'saudi-arabian-grand-prix' },
  { round: 3, name: 'Australia Grand Prix', circuit: 'Melbourne', date: 'Mar 24', image: TRACK_IMAGES['australian-grand-prix'] || MonacoGpImage, laps: 58, length: 'Melbourne', trackId: 'australian-grand-prix', rainProb: 0, grandPrixSlug: 'australian-grand-prix' },
  { round: 4, name: 'Japan Grand Prix', circuit: 'Suzuka', date: 'Apr 7', image: TRACK_IMAGES['japanese-grand-prix'] || MonacoGpImage, laps: 53, length: 'Suzuka', trackId: 'japanese-grand-prix', rainProb: 0, grandPrixSlug: 'japanese-grand-prix' },
  { round: 5, name: 'China Grand Prix', circuit: 'Shanghai', date: 'Apr 21', image: TRACK_IMAGES['chinese-grand-prix'] || MonacoGpImage, laps: 56, length: 'Shanghai', trackId: 'chinese-grand-prix', rainProb: 0, grandPrixSlug: 'chinese-grand-prix' },
  { round: 6, name: 'Miami Grand Prix', circuit: 'Miami', date: 'May 5', image: TRACK_IMAGES['miami-grand-prix'] || MonacoGpImage, laps: 57, length: 'Miami', trackId: 'miami-grand-prix', rainProb: 0, grandPrixSlug: 'miami-grand-prix' },
  { round: 7, name: 'Emilia Romagna Grand Prix', circuit: 'Imola', date: 'May 19', image: TRACK_IMAGES['emilia-romagna-grand-prix'] || MonacoGpImage, laps: 63, length: 'Imola', trackId: 'emilia-romagna-grand-prix', rainProb: 0, grandPrixSlug: 'emilia-romagna-grand-prix' },
  { round: 8, name: 'Monaco Grand Prix', circuit: 'Monte Carlo', date: 'May 26', image: TRACK_IMAGES['monaco-grand-prix'] || MonacoGpImage, laps: 78, length: 'Monte Carlo', trackId: 'monaco-grand-prix', rainProb: 0, grandPrixSlug: 'monaco-grand-prix' },
  { round: 9, name: 'Canada Grand Prix', circuit: 'Montreal', date: 'Jun 9', image: TRACK_IMAGES['canadian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Montreal', trackId: 'canadian-grand-prix', rainProb: 0, grandPrixSlug: 'canadian-grand-prix' },
  { round: 10, name: 'Spain Grand Prix', circuit: 'Barcelona', date: 'Jun 23', image: TRACK_IMAGES['spanish-grand-prix'] || MonacoGpImage, laps: 66, length: 'Barcelona', trackId: 'spanish-grand-prix', rainProb: 0, grandPrixSlug: 'spanish-grand-prix' },
  { round: 11, name: 'Austria Grand Prix', circuit: 'Spielberg', date: 'Jul 7', image: TRACK_IMAGES['austrian-grand-prix'] || MonacoGpImage, laps: 71, length: 'Spielberg', trackId: 'austrian-grand-prix', rainProb: 0, grandPrixSlug: 'austrian-grand-prix' },
  { round: 12, name: 'Great Britain Grand Prix', circuit: 'Silverstone', date: 'Jul 7', image: TRACK_IMAGES['british-grand-prix'] || MonacoGpImage, laps: 52, length: 'Silverstone', trackId: 'british-grand-prix', rainProb: 0, grandPrixSlug: 'british-grand-prix' },
  { round: 13, name: 'Hungary Grand Prix', circuit: 'Budapest', date: 'Jul 21', image: TRACK_IMAGES['hungarian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Budapest', trackId: 'hungarian-grand-prix', rainProb: 0, grandPrixSlug: 'hungarian-grand-prix' },
  { round: 14, name: 'Belgium Grand Prix', circuit: 'Spa', date: 'Aug 4', image: TRACK_IMAGES['belgian-grand-prix'] || MonacoGpImage, laps: 44, length: 'Spa', trackId: 'belgian-grand-prix', rainProb: 0, grandPrixSlug: 'belgian-grand-prix' },
  { round: 15, name: 'Netherlands Grand Prix', circuit: 'Zandvoort', date: 'Aug 18', image: TRACK_IMAGES['dutch-grand-prix'] || MonacoGpImage, laps: 72, length: 'Zandvoort', trackId: 'dutch-grand-prix', rainProb: 0, grandPrixSlug: 'dutch-grand-prix' },
  { round: 16, name: 'Italy Grand Prix', circuit: 'Monza', date: 'Sep 1', image: TRACK_IMAGES['italian-grand-prix'] || MonacoGpImage, laps: 53, length: 'Monza', trackId: 'italian-grand-prix', rainProb: 0, grandPrixSlug: 'italian-grand-prix' },
  { round: 17, name: 'Azerbaijan Grand Prix', circuit: 'Baku', date: 'Sep 15', image: TRACK_IMAGES['azerbaijan-grand-prix'] || MonacoGpImage, laps: 51, length: 'Baku', trackId: 'azerbaijan-grand-prix', rainProb: 0, grandPrixSlug: 'azerbaijan-grand-prix' },
  { round: 18, name: 'Singapore Grand Prix', circuit: 'Marina Bay', date: 'Sep 22', image: TRACK_IMAGES['singapore-grand-prix'] || MonacoGpImage, laps: 61, length: 'Marina Bay', trackId: 'singapore-grand-prix', rainProb: 0, grandPrixSlug: 'singapore-grand-prix' },
  { round: 19, name: 'United States Grand Prix', circuit: 'Austin', date: 'Oct 20', image: TRACK_IMAGES['united-states-grand-prix'] || MonacoGpImage, laps: 56, length: 'Austin', trackId: 'united-states-grand-prix', rainProb: 0, grandPrixSlug: 'united-states-grand-prix' },
  { round: 20, name: 'Mexico Grand Prix', circuit: 'Mexico City', date: 'Oct 27', image: TRACK_IMAGES['mexico-city-grand-prix'] || MonacoGpImage, laps: 71, length: 'Mexico City', trackId: 'mexico-city-grand-prix', rainProb: 0, grandPrixSlug: 'mexico-city-grand-prix' },
  { round: 21, name: 'Brazil Grand Prix', circuit: 'Interlagos', date: 'Nov 3', image: TRACK_IMAGES['sao-paulo-grand-prix'] || MonacoGpImage, laps: 71, length: 'Interlagos', trackId: 'sao-paulo-grand-prix', rainProb: 0, grandPrixSlug: 'sao-paulo-grand-prix' },
  { round: 22, name: 'Las Vegas Grand Prix', circuit: 'Las Vegas', date: 'Nov 23', image: TRACK_IMAGES['las-vegas-grand-prix'] || MonacoGpImage, laps: 62, length: 'Las Vegas', trackId: 'las-vegas-grand-prix', rainProb: 0, grandPrixSlug: 'las-vegas-grand-prix' },
  { round: 23, name: 'Qatar Grand Prix', circuit: 'Lusail', date: 'Dec 1', image: TRACK_IMAGES['qatar-grand-prix'] || MonacoGpImage, laps: 57, length: 'Lusail', trackId: 'qatar-grand-prix', rainProb: 0, grandPrixSlug: 'qatar-grand-prix' },
  { round: 24, name: 'Abu Dhabi Grand Prix', circuit: 'Yas Island', date: 'Dec 8', image: TRACK_IMAGES['abu-dhabi-grand-prix'] || MonacoGpImage, laps: 55, length: 'Yas Island', trackId: 'abu-dhabi-grand-prix', rainProb: 0, grandPrixSlug: 'abu-dhabi-grand-prix' },
];

const RACES_2025: Race[] = [
  { round: 1, name: 'Bahrain Grand Prix', circuit: 'Sakhir', date: 'Mar', image: TRACK_IMAGES['bahrain-grand-prix'] || MonacoGpImage, laps: 57, length: 'Sakhir', trackId: 'bahrain-grand-prix', rainProb: 0, grandPrixSlug: 'bahrain-grand-prix' },
  { round: 2, name: 'Saudi Arabia Grand Prix', circuit: 'Jeddah', date: 'Mar', image: TRACK_IMAGES['saudi-arabian-grand-prix'] || MonacoGpImage, laps: 50, length: 'Jeddah', trackId: 'saudi-arabian-grand-prix', rainProb: 0, grandPrixSlug: 'saudi-arabian-grand-prix' },
  { round: 3, name: 'Australia Grand Prix', circuit: 'Melbourne', date: 'Mar', image: TRACK_IMAGES['australian-grand-prix'] || MonacoGpImage, laps: 58, length: 'Melbourne', trackId: 'australian-grand-prix', rainProb: 0, grandPrixSlug: 'australian-grand-prix' },
  { round: 4, name: 'Japan Grand Prix', circuit: 'Suzuka', date: 'Apr', image: TRACK_IMAGES['japanese-grand-prix'] || MonacoGpImage, laps: 53, length: 'Suzuka', trackId: 'japanese-grand-prix', rainProb: 0, grandPrixSlug: 'japanese-grand-prix' },
  { round: 5, name: 'China Grand Prix', circuit: 'Shanghai', date: 'Apr', image: TRACK_IMAGES['chinese-grand-prix'] || MonacoGpImage, laps: 56, length: 'Shanghai', trackId: 'chinese-grand-prix', rainProb: 0, grandPrixSlug: 'chinese-grand-prix' },
  { round: 6, name: 'Miami Grand Prix', circuit: 'Miami', date: 'May', image: TRACK_IMAGES['miami-grand-prix'] || MonacoGpImage, laps: 57, length: 'Miami', trackId: 'miami-grand-prix', rainProb: 0, grandPrixSlug: 'miami-grand-prix' },
  { round: 7, name: 'Emilia Romagna Grand Prix', circuit: 'Imola', date: 'May', image: TRACK_IMAGES['emilia-romagna-grand-prix'] || MonacoGpImage, laps: 63, length: 'Imola', trackId: 'emilia-romagna-grand-prix', rainProb: 0, grandPrixSlug: 'emilia-romagna-grand-prix' },
  { round: 8, name: 'Monaco Grand Prix', circuit: 'Monte Carlo', date: 'May', image: TRACK_IMAGES['monaco-grand-prix'] || MonacoGpImage, laps: 78, length: 'Monte Carlo', trackId: 'monaco-grand-prix', rainProb: 0, grandPrixSlug: 'monaco-grand-prix' },
  { round: 9, name: 'Canada Grand Prix', circuit: 'Montreal', date: 'Jun', image: TRACK_IMAGES['canadian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Montreal', trackId: 'canadian-grand-prix', rainProb: 0, grandPrixSlug: 'canadian-grand-prix' },
  { round: 10, name: 'Spain Grand Prix', circuit: 'Barcelona', date: 'Jun', image: TRACK_IMAGES['spanish-grand-prix'] || MonacoGpImage, laps: 66, length: 'Barcelona', trackId: 'spanish-grand-prix', rainProb: 0, grandPrixSlug: 'spanish-grand-prix' },
  { round: 11, name: 'Austria Grand Prix', circuit: 'Spielberg', date: 'Jul', image: TRACK_IMAGES['austrian-grand-prix'] || MonacoGpImage, laps: 71, length: 'Spielberg', trackId: 'austrian-grand-prix', rainProb: 0, grandPrixSlug: 'austrian-grand-prix' },
  { round: 12, name: 'Great Britain Grand Prix', circuit: 'Silverstone', date: 'Jul', image: TRACK_IMAGES['british-grand-prix'] || MonacoGpImage, laps: 52, length: 'Silverstone', trackId: 'british-grand-prix', rainProb: 0, grandPrixSlug: 'british-grand-prix' },
  { round: 13, name: 'Hungary Grand Prix', circuit: 'Budapest', date: 'Jul', image: TRACK_IMAGES['hungarian-grand-prix'] || MonacoGpImage, laps: 70, length: 'Budapest', trackId: 'hungarian-grand-prix', rainProb: 0, grandPrixSlug: 'hungarian-grand-prix' },
  { round: 14, name: 'Belgium Grand Prix', circuit: 'Spa', date: 'Aug', image: TRACK_IMAGES['belgian-grand-prix'] || MonacoGpImage, laps: 44, length: 'Spa', trackId: 'belgian-grand-prix', rainProb: 0, grandPrixSlug: 'belgian-grand-prix' },
  { round: 15, name: 'Netherlands Grand Prix', circuit: 'Zandvoort', date: 'Aug', image: TRACK_IMAGES['dutch-grand-prix'] || MonacoGpImage, laps: 72, length: 'Zandvoort', trackId: 'dutch-grand-prix', rainProb: 0, grandPrixSlug: 'dutch-grand-prix' },
  { round: 16, name: 'Italy Grand Prix', circuit: 'Monza', date: 'Sep', image: TRACK_IMAGES['italian-grand-prix'] || MonacoGpImage, laps: 53, length: 'Monza', trackId: 'italian-grand-prix', rainProb: 0, grandPrixSlug: 'italian-grand-prix' },
  { round: 17, name: 'Azerbaijan Grand Prix', circuit: 'Baku', date: 'Sep', image: TRACK_IMAGES['azerbaijan-grand-prix'] || MonacoGpImage, laps: 51, length: 'Baku', trackId: 'azerbaijan-grand-prix', rainProb: 0, grandPrixSlug: 'azerbaijan-grand-prix' },
  { round: 18, name: 'Singapore Grand Prix', circuit: 'Marina Bay', date: 'Sep', image: TRACK_IMAGES['singapore-grand-prix'] || MonacoGpImage, laps: 61, length: 'Marina Bay', trackId: 'singapore-grand-prix', rainProb: 0, grandPrixSlug: 'singapore-grand-prix' },
  { round: 19, name: 'United States Grand Prix', circuit: 'Austin', date: 'Oct', image: TRACK_IMAGES['united-states-grand-prix'] || MonacoGpImage, laps: 56, length: 'Austin', trackId: 'united-states-grand-prix', rainProb: 0, grandPrixSlug: 'united-states-grand-prix' },
  { round: 20, name: 'Mexico Grand Prix', circuit: 'Mexico City', date: 'Oct', image: TRACK_IMAGES['mexico-city-grand-prix'] || MonacoGpImage, laps: 71, length: 'Mexico City', trackId: 'mexico-city-grand-prix', rainProb: 0, grandPrixSlug: 'mexico-city-grand-prix' },
  { round: 21, name: 'Brazil Grand Prix', circuit: 'Interlagos', date: 'Nov', image: TRACK_IMAGES['sao-paulo-grand-prix'] || MonacoGpImage, laps: 71, length: 'Interlagos', trackId: 'sao-paulo-grand-prix', rainProb: 0, grandPrixSlug: 'sao-paulo-grand-prix' },
  { round: 22, name: 'Las Vegas Grand Prix', circuit: 'Las Vegas', date: 'Nov', image: TRACK_IMAGES['las-vegas-grand-prix'] || MonacoGpImage, laps: 62, length: 'Las Vegas', trackId: 'las-vegas-grand-prix', rainProb: 0, grandPrixSlug: 'las-vegas-grand-prix' },
  { round: 23, name: 'Qatar Grand Prix', circuit: 'Lusail', date: 'Dec', image: TRACK_IMAGES['qatar-grand-prix'] || MonacoGpImage, laps: 57, length: 'Lusail', trackId: 'qatar-grand-prix', rainProb: 0, grandPrixSlug: 'qatar-grand-prix' },
  { round: 24, name: 'Abu Dhabi Grand Prix', circuit: 'Yas Island', date: 'Dec', image: TRACK_IMAGES['abu-dhabi-grand-prix'] || MonacoGpImage, laps: 55, length: 'Yas Island', trackId: 'abu-dhabi-grand-prix', rainProb: 0, grandPrixSlug: 'abu-dhabi-grand-prix' },
];

const probabilityValue = (prediction?: RaceWinPrediction | RacePrediction | SessionResultRow) => {
  if (!prediction) return 0;
  if ((prediction as any).pred_win_proba !== undefined) {
    const prob = (prediction as any).pred_win_proba_softmax ?? (prediction as any).pred_win_proba;
    return prob * 100;
  }
  if ((prediction as SessionResultRow).points !== undefined && (prediction as SessionResultRow).points !== null) {
    return (prediction as SessionResultRow).points as number;
  }
  return 0;
};

const slugify = (name: string) => {
  if (!name) return '';
  const lower = name
    .toLowerCase()
    .trim();
  return lower.replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
};

const prettyGrandPrix = (slug: string) => {
  if (!slug) return '';
  return slug
    .split('-')
    .map((part) => {
      if (part.toLowerCase() === 'gp') return part.toUpperCase();
      return part.charAt(0).toUpperCase() + part.slice(1);
    })
    .join(' ')
    .replace('Grand', 'Grand')
    .replace('Prix', 'Prix');
};

const formatDateRange = (start?: string | null, end?: string | null) => {
  if (!start && !end) return '';
  const formatter = new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric' });
  const startDateRaw = start ? new Date(start) : null;
  const endDateRaw = end ? new Date(end) : null;
  const startDate = startDateRaw && !Number.isNaN(startDateRaw.getTime()) ? startDateRaw : null;
  const endDate = endDateRaw && !Number.isNaN(endDateRaw.getTime()) ? endDateRaw : null;
  if (startDate && endDate) {
    const sameMonth = startDate.getMonth() === endDate.getMonth();
    const startLabel = formatter.format(startDate);
    const endLabel = sameMonth ? `${endDate.getDate()}` : formatter.format(endDate);
    return `${startLabel} – ${endLabel}, ${endDate.getFullYear()}`;
  }
  const single = startDate || endDate;
  return single ? `${formatter.format(single)}, ${single.getFullYear()}` : '';
};

const getTeamColor = (team?: string | null) => {
  if (!team) return '#94a3b8';
  const match = Object.keys(TEAM_COLORS).find((name) => name.toLowerCase() === team.toLowerCase());
  return match ? TEAM_COLORS[match] : '#94a3b8';
};

const findDriverVisual = (code?: string | null, name?: string | null, team?: string | null): Driver => {
  const upper = code?.toUpperCase() || '';
  if (upper && DRIVER_VISUAL_BY_CODE[upper]) {
    const visual = DRIVER_VISUAL_BY_CODE[upper];
    return { ...visual, team: team || visual.team, color: team ? getTeamColor(team) : visual.color };
  }
  if (name) {
    const last = name.split(' ').slice(-1)[0].toLowerCase();
    const match = Object.values(DRIVERS).find((d) => d.name.toLowerCase().includes(last));
    if (match) {
      return { ...match, team: team || match.team, color: team ? getTeamColor(team) : match.color };
    }
  }
  return { ...DRIVERS.verstappen, name: name || DRIVERS.verstappen.name, team: team || DRIVERS.verstappen.team, color: getTeamColor(team) };
};

const getTrackImage = (grandPrixSlug?: string | null) => {
  if (!grandPrixSlug) return LandingHeroImage;
  const slug = slugify(grandPrixSlug);
  if (TRACK_IMAGES[grandPrixSlug]) return TRACK_IMAGES[grandPrixSlug];
  if (TRACK_IMAGES[slug]) return TRACK_IMAGES[slug];
  return LandingHeroImage;
};

const raceFromMeta = (meta: any | null): Race => {
  if (!meta) {
    return {
      season: 2024,
      round: 1,
      name: 'Bahrain Grand Prix',
      circuit: 'Bahrain International Circuit',
      date: '',
      image: getTrackImage('bahrain-grand-prix'),
      laps: 0,
      length: 'Sakhir',
      trackId: 'bahrain',
      rainProb: 0,
      grandPrixSlug: 'bahrain-grand-prix',
    };
  }

  const slug = slugify(meta.grand_prix_slug || meta.display_name || '');

  // Fallback to static race definitions when API meta is missing laps/rain
  const fallbackByYear: Record<number, Race[]> = {
    2018: RACES_2018,
    2019: RACES_2019,
    2020: RACES_2020,
    2021: RACES_2021,
    2022: RACES_2022,
    2023: RACES_2023,
    2024: RACES_2024,
    2025: RACES_2025,
  };
  const fallbackCandidates = fallbackByYear[meta.season] || [];
  const fallback = fallbackCandidates.find((r) => {
    const rSlug = slugify(r.grandPrixSlug || r.trackId || r.name);
    return rSlug === slug || r.round === meta.round;
  });

  const laps = meta.laps ?? meta.lap_count ?? fallback?.laps ?? 0;
  const rainProb = meta.rain_probability ?? meta.rainProb ?? fallback?.rainProb ?? 0;
  const prettyName = meta.display_name || prettyGrandPrix(meta.grand_prix_slug || slug) || fallback?.name || 'Grand Prix';
  const circuitName = meta.circuit_name || fallback?.circuit || prettyName;
  const trackKey = meta.grand_prix_slug || slug || fallback?.grandPrixSlug || fallback?.trackId;

  return {
    season: meta.season,
    round: meta.display_round ?? meta.round ?? fallback?.round ?? 1,
    name: prettyName,
    circuit: circuitName,
    date: formatDateRange(meta.date_start, meta.date_end) || `${meta.season}`,
    image: getTrackImage(trackKey),
    laps,
    length: circuitName,
    trackId: slug || fallback?.trackId || 'circuit',
    rainProb,
    grandPrixSlug: slug,
  };
};

// --- Reusable Components ---

const Card = ({ title, children, className = '', actionIcon = null, onClick }: { title?: string, children: React.ReactNode, className?: string, actionIcon?: React.ReactNode, onClick?: () => void }) => (
  <div 
    onClick={onClick}
    className={`bg-slate-950/60 backdrop-blur-xl border border-white/5 rounded-2xl p-6 flex flex-col relative overflow-hidden group transition-all duration-300 ${onClick ? 'cursor-pointer hover:border-red-500/50 hover:shadow-[0_0_30px_rgba(239,68,68,0.1)]' : ''} ${className}`}
  >
    {/* Tech Corner Accents */}
    <div className="absolute top-0 right-0 p-2 opacity-20 group-hover:opacity-100 transition-opacity">
        <div className="w-2 h-2 border-t-2 border-r-2 border-white"></div>
    </div>
    <div className="absolute bottom-0 left-0 p-2 opacity-20 group-hover:opacity-100 transition-opacity">
        <div className="w-2 h-2 border-b-2 border-l-2 border-white"></div>
    </div>

    {title && (
      <div className="flex justify-between items-start mb-6 z-10 pr-4">
        <h3 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] italic group-hover:text-white transition-colors whitespace-nowrap">{title}</h3>
        {actionIcon || (onClick && <ArrowRight size={16} className="text-slate-600 group-hover:text-red-500 transition-colors -rotate-45 group-hover:rotate-0 transform duration-300 ml-4" />)}
      </div>
    )}
    <div className="z-10 relative flex-1">{children}</div>
    {/* Subtle gradient glow */}
    <div className="absolute -top-20 -right-20 w-64 h-64 bg-gradient-to-br from-white/5 to-transparent blur-[60px] rounded-full pointer-events-none group-hover:from-red-600/10 transition-colors duration-500"></div>
  </div>
);

const Badge = ({ children, color = 'neutral' }: { children: React.ReactNode, color?: 'neutral' | 'green' | 'red' | 'blue' | 'yellow' | 'cyan' }) => {
  const colors = {
    neutral: 'bg-slate-800/50 text-slate-300 border-slate-700/50',
    green: 'bg-green-950/50 text-green-400 border-green-500/30 shadow-[0_0_10px_rgba(34,197,94,0.1)]',
    red: 'bg-red-950/50 text-red-500 border-red-500/30 shadow-[0_0_10px_rgba(239,68,68,0.1)]',
    blue: 'bg-blue-950/50 text-blue-400 border-blue-500/30 shadow-[0_0_10px_rgba(59,130,246,0.1)]',
    yellow: 'bg-yellow-950/50 text-yellow-400 border-yellow-500/30 shadow-[0_0_10px_rgba(234,179,8,0.1)]',
    cyan: 'bg-cyan-950/50 text-cyan-400 border-cyan-500/30 shadow-[0_0_10px_rgba(6,182,212,0.1)]',
  };
  return (
    <span className={`px-2 py-0.5 rounded-sm text-[10px] font-black uppercase tracking-wider italic border backdrop-blur-md ${colors[color]}`}>
      {children}
    </span>
  );
};

type ProgressBarProps = {
  value: number;
  max?: number;
  color?: string;
  height?: string;
};

const ProgressBar = ({ value, max = 100, color = 'from-blue-600 to-blue-400', height = 'h-1.5' }: ProgressBarProps) => (
  <div className={`w-full bg-slate-800 rounded-sm ${height} overflow-hidden skew-x-[-10deg]`}>
    <div className={`h-full bg-gradient-to-r ${color} transition-all duration-1000 ease-out relative`} style={{ width: `${(value / max) * 100}%` }}>
      <div className="absolute right-0 top-0 h-full w-2 bg-white/50 blur-[2px]"></div>
    </div>
  </div>
);

// History-specific UI components (keep styling, feed live data)
// HistoryTeamCard styling now handled inline in HistoryView

const TelemetryDrawer = ({ team, onClose }: { team: any; onClose: () => void }) => {
  if (!team) return null;
  const d1 = team.drivers[0];
  const d2 = team.drivers[1];

  return (
    <motion.div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center p-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      <motion.div
        layoutId={`card-${team.id}`}
        className="relative w-full max-w-4xl overflow-hidden rounded-3xl border border-neutral-800 bg-[#0a0a0a] shadow-2xl"
        style={{ borderColor: team.color }}
      >
        <div className="flex items-center justify-between border-b border-neutral-800 bg-black/40 px-6 py-4 backdrop-blur-xl">
          <div className="flex items-center gap-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg font-bold text-black shadow-[0_0_15px_rgba(0,0,0,0.5)]" style={{ background: team.color }}>
              {team.shortName}
            </div>
            <div>
              <h2 className="text-2xl font-black uppercase italic tracking-tighter text-white">{team.name}</h2>
              <div className="flex items-center gap-2 text-xs font-medium text-neutral-400">
                <Activity className="h-3 w-3 text-green-500" />
                <span>LIVE TELEMETRY</span>
              </div>
            </div>
          </div>
          <button onClick={onClose} className="rounded-full bg-neutral-900 p-2 text-neutral-400 hover:bg-neutral-800 hover:text-white transition-colors">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-0">
          <div className="md:col-span-5 border-r border-neutral-800 bg-neutral-900/20 p-6">
            <h3 className="mb-6 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-neutral-400">
              <Users className="h-4 w-4" />
              Teammate Battle
            </h3>

            <div className="flex justify-between items-end mb-8 px-4">
              {[d1, d2].map((d, idx) => (
                <div key={d?.name || idx} className="flex flex-col items-center">
                  <div className="w-16 h-16 rounded-full border-2 border-neutral-700 overflow-hidden mb-2 shadow-lg">
                    <img src={d?.image} className="w-full h-full object-cover" />
                  </div>
                  <span className="text-xs font-bold text-white uppercase">{d?.name?.split(' ').pop()}</span>
                  <span className="text-[10px] text-neutral-500">#{d?.number || '--'}</span>
                </div>
              ))}
            </div>

            <div className="space-y-6">
              <BattleBar label="Points" v1={d1?.points || 0} v2={d2?.points || 0} max={Math.max(d1?.points || 0, d2?.points || 0, 1)} color={team.color} />
              <BattleBar label="Wins" v1={d1?.wins || 0} v2={d2?.wins || 0} max={Math.max(d1?.wins || 0, d2?.wins || 0, 1)} color={team.color} />
              <BattleBar label="Podiums" v1={d1?.podiums || 0} v2={d2?.podiums || 0} max={Math.max(d1?.podiums || 0, d2?.podiums || 0, 1)} color={team.color} />
            </div>
          </div>

          <div className="md:col-span-7 p-6 relative overflow-hidden">
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:20px_20px] pointer-events-none" />

            <h3 className="mb-6 flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-neutral-400 relative z-10">
              <TrendingUp className="h-4 w-4" />
              Season Trajectory
            </h3>

            <div className="relative h-64 w-full rounded-xl border border-neutral-800 bg-black/50 p-4 backdrop-blur-sm">
              <div className="flex h-full items-end gap-2">
                {buildTrajectory(team).map((pts: number, i: number) => (
                  <div key={i} className="group relative flex-1 flex flex-col justify-end h-full">
                    <motion.div
                      initial={{ height: 0 }}
                      animate={{ height: `${pts}%` }}
                      transition={{ duration: 0.8, delay: i * 0.05 }}
                      className="w-full rounded-t-sm opacity-80 hover:opacity-100 transition-opacity relative"
                      style={{ background: team.color }}
                    >
                      <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 bg-neutral-800 text-white text-[10px] py-1 px-2 rounded pointer-events-none transition-opacity font-mono">
                        {pts.toFixed(1)} PTS
                      </div>
                    </motion.div>
                    <div className="mt-2 text-center text-[10px] font-mono text-neutral-600">R{i + 1}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-6 grid grid-cols-3 gap-4">
              <div className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-3">
                <div className="text-[10px] uppercase text-neutral-500 mb-1 flex items-center gap-1">
                  <Trophy className="w-3 h-3" /> Wins
                </div>
                <div className="text-xl font-bold text-white">{(team.drivers || []).reduce((acc: number, d: any) => acc + (d.wins || 0), 0)}</div>
              </div>
              <div className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-3">
                <div className="text-[10px] uppercase text-neutral-500 mb-1 flex items-center gap-1">
                  <Zap className="w-3 h-3" /> Podiums
                </div>
                <div className="text-xl font-bold text-white">{(team.drivers || []).reduce((acc: number, d: any) => acc + (d.podiums || 0), 0)}</div>
              </div>
              <div className="rounded-lg border border-neutral-800 bg-neutral-900/50 p-3">
                <div className="text-[10px] uppercase text-neutral-500 mb-1 flex items-center gap-1">
                  <Timer className="w-3 h-3" /> Consistency
                </div>
                <div className="text-xl font-bold text-white">—</div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

const DriverModal = ({ driver, onClose, paceMap }: { driver: Driver | null, onClose: () => void, paceMap?: DriverPaceMap }) => {
  if (!driver) return null;
  const code = DRIVER_CODE_LOOKUP[driver.id] || driver.id.toUpperCase();
  const positions = paceMap?.[code] || [];
  const rankDisplay = driver.rank ?? (driver.points ? 1 : 0);
  const winsDisplay = driver.seasonWins ?? driver.careerWins;
  const podiumDisplay = driver.seasonPodiums ?? driver.podiums;
  const countryCode = driver.country === 'UK' ? 'GB' : (driver.country || 'GB');
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xl animate-in fade-in duration-300" onClick={onClose}>
      <div className="bg-[#0a0a0a] border border-white/10 w-full max-w-2xl rounded-3xl overflow-hidden relative shadow-[0_0_100px_rgba(0,0,0,0.8)] animate-in slide-in-from-bottom-10 duration-300" onClick={e => e.stopPropagation()}>
        <button onClick={onClose} className="absolute top-6 right-6 p-2 bg-white/5 hover:bg-white/10 rounded-full transition-colors text-white z-20 backdrop-blur-md border border-white/10">
          <X size={20} />
        </button>
        
        {/* Header Background */}
        <div className="h-48 relative overflow-hidden">
          <div className="absolute inset-0 opacity-40 mix-blend-screen" style={{backgroundColor: driver.color, backgroundImage: `linear-gradient(45deg, transparent 25%, rgba(0,0,0,0.5) 25%, rgba(0,0,0,0.5) 50%, transparent 50%, transparent 75%, rgba(0,0,0,0.5) 75%, rgba(0,0,0,0.5))`}}></div>
          <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-transparent to-transparent"></div>
          <h1 className="absolute -bottom-4 -left-4 text-[10rem] font-black text-white italic opacity-10 tracking-tighter leading-none" style={{WebkitTextStroke: '2px rgba(255,255,255,0.1)', color: 'transparent'}}>{driver.number}</h1>
        </div>

        <div className="px-10 pb-10 -mt-20 relative z-10 flex gap-8 items-end">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent rounded-2xl z-10"></div>
            <img src={driver.image} className="w-40 h-40 rounded-2xl border-2 border-white/10 bg-slate-900 object-cover shadow-2xl relative z-0" />
            <div className="absolute bottom-2 left-2 z-20">
               <img src={`https://purecatamphetamine.github.io/country-flag-icons/3x2/${countryCode}.svg`} className="w-6 rounded-sm shadow-sm" />
            </div>
          </div>
          
          <div className="mb-2 flex-1">
            <div className="flex items-center gap-3 mb-1">
              <h2 className="text-5xl font-black text-white leading-none italic tracking-tighter uppercase">{driver.name.split(' ')[1]}</h2>
            </div>
            <p className="text-slate-400 text-xl font-bold uppercase tracking-widest">{driver.team}</p>
          </div>
          <div className="ml-auto mb-4 text-right">
             <div className="text-5xl font-mono font-black text-white tracking-tighter italic" style={{textShadow: `0 0 30px ${driver.color}60`}}>{driver.points}<span className="text-sm font-sans text-slate-500 font-bold ml-1 not-italic">PTS</span></div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-1 px-10 mb-10">
           {/* Stat Cards with "Cut" corners via skew */}
           <div className="bg-slate-900/50 p-5 border-l-2 border-white/10 backdrop-blur-md relative overflow-hidden group hover:bg-white/5 transition-colors">
             <div className="text-[10px] text-slate-500 uppercase tracking-widest font-black mb-1">Rank</div>
             <div className="text-3xl font-black text-white italic">P{rankDisplay || '—'}</div>
           </div>
           <div className="bg-slate-900/50 p-5 border-l-2 border-white/10 backdrop-blur-md relative overflow-hidden group hover:bg-white/5 transition-colors">
             <div className="text-[10px] text-slate-500 uppercase tracking-widest font-black mb-1">Wins</div>
             <div className="text-3xl font-black text-white italic">{winsDisplay}</div>
           </div>
           <div className="bg-slate-900/50 p-5 border-l-2 border-white/10 backdrop-blur-md relative overflow-hidden group hover:bg-white/5 transition-colors">
             <div className="text-[10px] text-slate-500 uppercase tracking-widest font-black mb-1">Podiums</div>
             <div className="text-3xl font-black text-white italic">{podiumDisplay}</div>
           </div>
        </div>
        
        <div className="px-10 pb-10">
          <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-4">Season Pace (2024)</h3>
          <div className="h-32 flex items-end justify-between gap-1">
            {(positions.length ? positions.slice(0, 14) : [4,2,1,1,3,5,2,1,1,6,2,1,4,2]).map((pos, i) => (
              <div key={i} className="flex-1 bg-slate-800 hover:bg-white transition-all duration-300 relative group skew-x-[-10deg]" style={{height: `${(21 - pos) * 5}%`}}>
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 mb-2 text-white text-[10px] font-bold opacity-0 group-hover:opacity-100 transition-opacity skew-x-[10deg]">
                  P{pos}
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}

// --- Sub-Views ---

const HomeView = ({
  setTab,
  activeRace,
  topPredictions,
  raceResults,
  raceWeather,
  sessions,
  selectedSessionType,
  standingsLeader,
}: {
  setTab: (t: string) => void;
  activeRace: Race;
  topPredictions: (RacePrediction | SessionResultRow)[];
  raceResults: SessionResultRow[];
  raceWeather: WeatherSummary;
  sessions: SessionMeta[];
  selectedSessionType: string;
  standingsLeader?: DriverStanding | null;
}) => {
  const sorted = topPredictions
    .slice()
    .sort((a, b) => probabilityValue(b) - probabilityValue(a));
  const top1 = sorted[0];
  const top2 = sorted[1];
  const top3 = sorted[2];

  const topDriverMock = findDriverVisual((top1 as any)?.driver_code, (top1 as any)?.driver_name, (top1 as any)?.team_name);
  const topProb = top1 ? probabilityValue(top1).toFixed(1) : '100';
  const secondProb = top2 ? probabilityValue(top2) : 24;
  const thirdProb = top3 ? probabilityValue(top3) : 12;

  const secondLabel = top2?.driver_name || top2?.driver_code || 'Norris';
  const thirdLabel = top3?.driver_name || top3?.driver_code || 'Leclerc';

  const activeSession = sessions.find((s) => s.session_type === selectedSessionType) || sessions[0];
  const sessionLabel = activeSession ? `${activeSession.session_type} ${activeSession.name ? `· ${activeSession.name}` : ''}` : 'Race Weekend';
  const leaderLabel = standingsLeader ? standingsLeader.driver_code || standingsLeader.driver_name : '—';
  const rainValueRaw = raceWeather.rain ?? raceWeather.humidity ?? activeRace.rainProb ?? 0;
  const rainValue = Number.isFinite(Number(rainValueRaw)) ? Number(rainValueRaw) : 0;
  const airTemp = raceWeather.airTemp ?? raceWeather.trackTemp;
  const trackTemp = raceWeather.trackTemp ?? raceWeather.airTemp;
  const derivedLapsFromResults = raceResults.reduce((max, r) => Math.max(max, r.laps ?? 0), 0);
  const derivedLaps = Math.max(
    activeRace.laps || 0,
    derivedLapsFromResults,
    topPredictions.reduce((max, p) => Math.max(max, (p as any).laps ?? 0), 0)
  );
  const lapsDisplay = derivedLaps || '—';

  return (
  <div className="space-y-6 animate-in fade-in duration-500">
    {/* Hero Section - Upcoming Race */}
    <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
      <Card 
        onClick={() => setTab('race')}
        className="md:col-span-8 !bg-cover !bg-center relative !border-red-500/20 overflow-hidden" 
        title="Next Grand Prix"
        actionIcon={<div className="flex items-center gap-2 text-red-500 font-bold text-xs uppercase tracking-widest animate-pulse"><div className="w-2 h-2 bg-red-500 rounded-full"></div>Live</div>}
      >
        {/* Dynamic Background Image */}
        <div className="absolute inset-0 z-0 flex items-center justify-center overflow-hidden bg-[#0b0f1a]">
           <img
             src={activeRace.image || getTrackImage(activeRace.grandPrixSlug)}
             className="w-full h-full object-contain object-center opacity-95 transition-transform duration-[20s] mix-blend-normal"
             style={{ filter: 'saturate(1.03) contrast(1.02)' }}
             loading="lazy"
           />
           <div className="absolute inset-0 bg-gradient-to-r from-black/65 via-black/35 to-transparent"></div>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-end relative z-10 h-full min-h-[300px]">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Flag className="text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]" size={20} />
              <span className="text-lg font-bold text-red-500 tracking-widest uppercase">{activeRace.name}</span>
            </div>
            <h1 className="text-7xl font-black text-white mb-2 tracking-tighter leading-none italic transform -skew-x-6 drop-shadow-2xl">{activeRace.circuit}</h1>
            <p className="text-slate-300 flex items-center gap-6 text-xs font-bold uppercase tracking-wider drop-shadow-md">
              <span className="flex items-center gap-2"><Calendar size={14} className="text-red-500" /> {activeRace.date || activeRace.season}</span>
              <span className="flex items-center gap-2"><MapIcon size={14} className="text-red-500" /> Round {activeRace.round}</span>
            </p>
          </div>
          <div className="mt-8 md:mt-0 flex gap-4 text-center">
             <div className="bg-black/60 p-4 border-l-2 border-red-500 backdrop-blur-md min-w-[100px]">
              <div className="text-3xl font-black text-white italic">{lapsDisplay}</div>
              <div className="text-[9px] uppercase text-slate-500 font-black tracking-widest">Laps</div>
            </div>
             <div className="bg-black/60 p-4 border-l-2 border-blue-500 backdrop-blur-md min-w-[100px]">
            <div className="text-3xl font-black text-white italic">{rainValue !== undefined && rainValue !== null ? rainValue.toFixed(0) : activeRace.rainProb}<span className="text-sm">%</span></div>
              <div className="text-[9px] uppercase text-slate-500 font-black tracking-widest">Rain</div>
            </div>
          </div>
        </div>
      </Card>

      <Card 
        onClick={() => setTab('predictions')}
        className="md:col-span-4 !border-blue-500/20 relative" 
        title="Predictive AI"
        actionIcon={<Zap size={18} className="text-blue-400" />}
      >
        <div className="flex flex-col h-full justify-between relative z-10">
          <div className="flex items-center gap-5">
            <div className="relative">
              <img src={topDriverMock.image} className="w-16 h-16 rounded-xl border-2 border-blue-500 object-cover bg-slate-900 shadow-[0_0_20px_rgba(59,130,246,0.4)]" />
              <div className="absolute -bottom-1 -right-1 bg-blue-600 text-white text-[9px] font-black px-1.5 py-0.5 border border-black italic">P1</div>
            </div>
            <div>
              <div className="text-5xl font-black text-white tracking-tighter italic leading-none" style={{textShadow: '0 0 20px rgba(59,130,246,0.5)'}}>{topProb}%</div>
              <div className="text-xs text-blue-400 font-black uppercase tracking-widest">Win Prob</div>
            </div>
          </div>
          <div className="mt-6 space-y-4">
             <div className="space-y-1">
               <div className="flex justify-between text-[10px] font-bold uppercase tracking-wider">
                 <span className="text-slate-300">{secondLabel}</span>
                 <span className="text-orange-500">{secondProb.toFixed ? secondProb.toFixed(1) : secondProb}%</span>
               </div>
               <ProgressBar value={secondProb} color="from-orange-500 to-orange-400" />
             </div>
             <div className="space-y-1">
               <div className="flex justify-between text-[10px] font-bold uppercase tracking-wider">
                 <span className="text-slate-300">{thirdLabel}</span>
                 <span className="text-red-500">{thirdProb.toFixed ? thirdProb.toFixed(1) : thirdProb}%</span>
               </div>
               <ProgressBar value={thirdProb} color="from-red-600 to-red-500" />
             </div>
          </div>
        </div>
      </Card>
    </div>

    {/* Quick Stats Grid */}
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card title="Status" onClick={() => setTab('race')} className="!border-green-500/20 !bg-green-950/10">
        <div className="flex items-center gap-3 text-green-400 font-black text-xl italic tracking-tighter">
           <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.8)]"></div> {sessionLabel || 'Ready'}
        </div>
        <p className="text-[10px] text-slate-500 mt-2 font-bold uppercase tracking-widest">Weekend Schedule</p>
      </Card>
      <Card title="Air" onClick={() => setTab('race')}>
        <div className="flex items-center gap-3 text-white font-black text-xl italic">
           <Wind size={20} className="text-slate-400" /> {airTemp !== undefined && airTemp !== null ? `${airTemp.toFixed(0)}°C` : '—'}
        </div>
        <p className="text-[10px] text-slate-500 mt-2 font-bold uppercase tracking-widest">Ambient</p>
      </Card>
      <Card title="Track" onClick={() => setTab('race')} className="!border-orange-500/20">
        <div className="flex items-center gap-3 text-white font-black text-xl italic">
           <Thermometer size={20} className="text-orange-500" /> {trackTemp !== undefined && trackTemp !== null ? `${trackTemp.toFixed(0)}°C` : '—'}
        </div>
        <p className="text-[10px] text-slate-500 mt-2 font-bold uppercase tracking-widest">Track Temp</p>
      </Card>
       <Card title="Defending" onClick={() => setTab('standings')} className="!border-yellow-500/20">
        <div className="flex items-center gap-3 text-white font-black text-xl italic">
           <Trophy size={20} className="text-yellow-400" /> {leaderLabel || '---'}
        </div>
        <p className="text-[10px] text-slate-500 mt-2 font-bold uppercase tracking-widest">{standingsLeader?.driver_name || 'Drivers Leader'}</p>
      </Card>
    </div>
  </div>
  );
};

const TeamsView = ({ teamStandings }: { teamStandings: TeamStanding[] }) => {
  const getTeamColor = (teamName: string): string => {
    return TEAM_COLORS[teamName] || '#FFFFFF';
  };

  const DriverBar = ({ drivers, teamColor }: { drivers: Array<{driver_code: string; driver_name: string; points: number; races: number}>, teamColor: string }) => {
    const totalPoints = drivers.reduce((acc, d) => acc + d.points, 0) || 1;
    const driver1Pct = (drivers[0].points / totalPoints) * 100;
    
    return (
      <div className="mt-4 space-y-2">
        <div className="flex justify-between text-xs text-slate-400 font-mono uppercase tracking-wider">
          <span>{drivers[0].driver_code}</span>
          <span className="text-white/30">vs</span>
          <span>{drivers[1]?.driver_code || '---'}</span>
        </div>
        <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex relative">
          <div 
            className="h-full relative group transition-all duration-1000 ease-out"
            style={{ width: `${driver1Pct}%`, backgroundColor: teamColor }}
          >
            <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
          </div>
          <div className="h-full flex-1 bg-slate-700/50" />
          <div 
            className="absolute h-full w-0.5 bg-black/80 z-10" 
            style={{ left: `${driver1Pct}%` }} 
          />
        </div>
        <div className="flex justify-between text-[10px] text-slate-500 font-mono">
          <span>{drivers[0].points.toFixed(0)} PTS</span>
          <span>{drivers[1]?.points.toFixed(0) || '0'} PTS</span>
        </div>
      </div>
    );
  };

  const TeamCard = ({ team, isHero = false, delay = 0 }: { team: TeamStanding, isHero?: boolean, delay?: number }) => {
    const [mounted, setMounted] = useState(false);
    const teamColor = getTeamColor(team.team_name);

    useEffect(() => {
      const timer = setTimeout(() => setMounted(true), delay);
      return () => clearTimeout(timer);
    }, [delay]);

    return (
      <div 
        className={`relative group rounded-3xl overflow-hidden backdrop-blur-md border border-white/10 transition-all duration-300 ease-out cursor-pointer will-change-transform hover:-translate-y-2 ${
          mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
        } ${isHero ? 'md:col-span-2 md:row-span-1' : ''}`}
        style={{ 
          background: `linear-gradient(145deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.4) 100%)`,
          boxShadow: `0 10px 20px -10px rgba(0,0,0,0.5)`
        }}
      >
        <div 
          className="absolute top-0 left-0 w-full h-[2px] transition-all duration-300 opacity-30 group-hover:opacity-100"
          style={{ 
            background: `linear-gradient(90deg, transparent, ${teamColor}, transparent)`
          }}
        />

        <div className="p-6 h-full flex flex-col justify-between relative z-10">
          <div className="flex justify-between items-start">
            <div className="flex items-center space-x-3">
              <div className="text-3xl font-bold text-white/10 font-mono -ml-1 select-none">
                P{team.position}
              </div>
              <div>
                <h3 className="text-white font-bold text-lg tracking-wide uppercase italic">{team.team_name}</h3>
                <p className="text-slate-400 text-xs font-mono">{team.drivers.length} Drivers</p>
              </div>
            </div>
            
            <div className="w-12 h-12 relative flex items-center justify-center">
              <div 
                className="absolute inset-0 rounded-full opacity-20 blur-md transition-opacity duration-300 group-hover:opacity-40" 
                style={{ backgroundColor: teamColor }} 
              />
              <div className="w-full h-full flex items-center justify-center font-bold text-xl text-white rounded-full bg-white/5 border border-white/10 relative z-10">
                {team.team_name[0]}
              </div>
            </div>
          </div>

          {isHero && (
            <div className="my-6 hidden md:block">
              <div className="flex items-end space-x-2 mb-2">
                <span className="text-xs text-green-400 font-mono uppercase flex items-center">
                  <Zap size={12} className="mr-1" />
                  Championship Leader
                </span>
                <div className="h-[1px] flex-1 bg-gradient-to-r from-green-500/50 to-transparent"></div>
              </div>
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

          <div className="mt-6">
            <div className="flex items-baseline justify-between">
              <div>
                <span className="text-xs text-slate-500 font-mono uppercase tracking-widest block mb-1">Total Points</span>
                <span 
                  className="text-5xl font-light tracking-tighter text-white transition-all duration-300"
                  style={{ textShadow: '0 0 0px transparent' }}
                >
                  {team.points.toFixed(0)}
                </span>
              </div>
              {!isHero && (
                <div className="flex flex-col items-end">
                  <span className="text-xs text-slate-500 mb-1">Rank</span>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border border-white/10 ${team.position <= 3 ? 'bg-white/10 text-white' : 'bg-slate-800 text-slate-400'}`}>
                    {team.position}
                  </div>
                </div>
              )}
            </div>

            {team.drivers.length >= 2 && <DriverBar drivers={team.drivers} teamColor={teamColor} />}
          </div>
        </div>
        
        <div 
          className="absolute inset-0 opacity-[0.03] z-0 pointer-events-none"
          style={{ 
            backgroundImage: `radial-gradient(circle at 100% 100%, ${teamColor}, transparent 50%)`
          }}
        />
      </div>
    );
  };

  if (teamStandings.length === 0) {
    return (
      <div className="text-center py-20 text-slate-500">
        <Database size={48} className="mx-auto mb-4 opacity-50" />
        <p className="text-lg font-mono uppercase tracking-widest">No team data available</p>
      </div>
    );
  }

  return (
    <div className="animate-in fade-in duration-300">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {teamStandings.length > 0 && <TeamCard team={teamStandings[0]} isHero={true} delay={0} />}
        {teamStandings.slice(1, 3).map((team, index) => (
          <TeamCard key={team.team_name} team={team} delay={100 + (index * 100)} />
        ))}
        {teamStandings.slice(3).map((team, index) => (
          <TeamCard key={team.team_name} team={team} delay={300 + (index * 50)} />
        ))}
      </div>
      
      <div className="mt-12 border-t border-white/5 pt-8 text-center">
        <p className="text-xs text-slate-600 font-mono">
          LAKEHOUSE PROJECT // TELEMETRY MODULE V2.5 // DATA SOURCE: OFFICIAL F1 API
        </p>
      </div>
    </div>
  );
};

const normalizeTeamName = (name?: string | null) => (name || '').toLowerCase().replace(/[^a-z0-9]/g, '');
const TEAM_NAME_CANON_2024 = new Map<string, string>([
  ['rb', 'VCARB'],
  ['racingbulls', 'VCARB'],
  ['rbracing', 'VCARB'],
  ['rbracingteam', 'VCARB'],
  ['visacashapprb', 'VCARB'],
  ['rbf1team', 'VCARB'],
  ['vcarb', 'VCARB'],
]);
const TEAM_NAME_CANON_2025 = new Map<string, string>([
  ['redbullracing', 'Red Bull Racing'],
  ['ferrari', 'Ferrari'],
  ['mercedes', 'Mercedes'],
  ['mclaren', 'McLaren'],
  ['astonmartin', 'Aston Martin'],
  ['rb', 'Racing Bulls'],
  ['rbracing', 'Racing Bulls'],
  ['rbracingteam', 'Racing Bulls'],
  ['racingbulls', 'Racing Bulls'],
  ['visacashapprb', 'Racing Bulls'],
  ['rbf1team', 'Racing Bulls'],
  ['alpine', 'Alpine'],
  ['williams', 'Williams'],
  ['kicksauber', 'Kick Sauber'],
  ['sauber', 'Kick Sauber'],
  ['haasf1team', 'Haas F1 Team'],
  ['haas', 'Haas F1 Team'],
]);
const ALLOWED_2025_TEAMS = new Set(
  [
    'Red Bull Racing',
    'Ferrari',
    'Mercedes',
    'McLaren',
    'Aston Martin',
    'RB',
    'RB F1 Team',
    'Visa Cash App RB',
    'Racing Bulls',
    'Alpine',
    'Williams',
    'Kick Sauber',
    'Haas F1 Team',
  ].map(normalizeTeamName)
);

const StandingsView = ({ driverStandings, constructorStandings, driverPace, season }: { driverStandings: DriverStanding[], constructorStandings: ConstructorStanding[], driverPace: DriverPaceMap, season?: number | null }) => {
  const [selectedDriver, setSelectedDriver] = useState<Driver | null>(null);

  const driverRows = driverStandings.length
    ? driverStandings.map((d, idx) => {
        const visual = findDriverVisual(d.driver_code, d.driver_name, d.team_name);
        return { ...d, color: visual.color || getTeamColor(d.team_name), image: visual.image, rank: idx + 1 };
      })
    : Object.values(DRIVERS).map((d, idx) => ({
        position: idx + 1,
        driver_code: d.id,
        driver_name: d.name,
        team_name: d.team,
        points: d.points,
        wins: Math.max(0, Math.floor(d.points / 100)),
        podiums: Math.max(0, Math.floor(d.points / 50)),
        color: d.color,
        image: d.image,
        rank: idx + 1,
      }));

  const filterConstructorsBySeason = (rows: ConstructorStanding[]) => {
    const currentSeason = season ?? new Date().getFullYear();
    const seenRaw = new Set<string>();
    const seenCanon = new Set<string>();
    return rows
      .filter((c) => {
        const norm = normalizeTeamName(c.team_name);
        if (seenRaw.has(norm)) return false;
        seenRaw.add(norm);
        if (currentSeason >= 2025) {
          return ALLOWED_2025_TEAMS.has(norm);
        }
        return true;
      })
      .map((c) => {
        const norm = normalizeTeamName(c.team_name);
        const canonical = currentSeason >= 2025
          ? TEAM_NAME_CANON_2025.get(norm) || c.team_name
          : currentSeason === 2024
            ? TEAM_NAME_CANON_2024.get(norm) || c.team_name
            : c.team_name;
        const canonNorm = normalizeTeamName(canonical);
        if (currentSeason >= 2025 || currentSeason === 2024) {
          if (seenCanon.has(canonNorm)) return null;
          seenCanon.add(canonNorm);
        }
        return { ...c, team_name: canonical, color: getTeamColor(canonical) };
      })
      .filter(Boolean) as ConstructorStanding[];
  };

  const constructorRows = constructorStandings.length
    ? filterConstructorsBySeason(constructorStandings)
    : filterConstructorsBySeason(
        TEAMS.map((t, idx) => ({
          position: idx + 1,
          team_name: t.fullTeamName,
          points: t.points,
          color: t.color,
        }))
      );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in duration-500">
      <DriverModal driver={selectedDriver} onClose={() => setSelectedDriver(null)} paceMap={driverPace} />
      
      <Card title="Driver Standings" className="!border-cyan-500/20 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-slate-500 border-b border-white/5 text-[10px] uppercase tracking-widest bg-black/20">
                <th className="py-4 pl-6 font-black">Pos</th>
                <th className="py-4 font-black">Driver</th>
                <th className="py-4 text-right font-black">Pts</th>
                <th className="py-4 text-right font-black pr-6">Wins</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {driverRows.sort((a,b) => b.points - a.points).map((driver, idx) => (
                <tr 
                  key={driver.driver_code} 
                  onClick={() => setSelectedDriver({
                    id: driver.driver_code.toLowerCase(),
                    name: driver.driver_name,
                    team: driver.team_name,
                    number: driver.rank || idx + 1,
                    color: (driver as any).color || getTeamColor(driver.team_name),
                    points: driver.points,
                    country: (driver as any).country_code || 'UNK',
                    image: (driver as any).image,
                    careerWins: driver.wins ?? 0,
                    titles: 0,
                    poles: 0,
                    podiums: driver.podiums ?? 0,
                    fastestLaps: 0,
                    grandPrix: driverPace[driver.driver_code]?.length ?? 0,
                    rank: driver.rank || idx + 1,
                    seasonWins: driver.wins ?? 0,
                    seasonPodiums: driver.podiums ?? 0,
                  })}
                  className="group hover:bg-white/5 transition-all duration-200 cursor-pointer"
                >
                  <td className="py-4 pl-6 text-slate-400 font-mono font-bold group-hover:text-white transition-colors text-lg italic">{driver.rank || idx + 1}</td>
                  <td className="py-4">
                    <div className="flex items-center gap-4">
                      <div className="w-1 h-8 skew-x-[-12deg]" style={{backgroundColor: driver.color || '#fff', boxShadow: `0 0 10px ${(driver as any).color || '#fff'}80`}}></div>
                      <div>
                        <div className="font-black text-white group-hover:text-cyan-400 transition-colors uppercase italic tracking-wider">{driver.driver_name.split(' ').slice(-1).join(' ')}</div>
                        <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{driver.team_name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 text-right font-mono font-black text-lg text-white italic">{driver.points.toFixed ? driver.points.toFixed(0) : driver.points}</td>
                  <td className="py-4 text-right text-slate-500 font-bold pr-6">{driver.wins ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
      <Card title="Constructors" className="!border-blue-500/20">
          <div className="space-y-4 pt-2">
             {constructorRows.map((team, idx) => {
               const teamName = team.team_name || (team as any).name;
               const teamIcon = TEAM_ICONS[teamName];
               return (
                 <div key={teamName} className="relative group cursor-pointer p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-all duration-300 border border-white/5 hover:border-white/20">
                   <div className="flex justify-between items-start mb-2 relative z-10">
                     <div className="flex items-center gap-3">
                       {teamIcon && (
                         <div className="w-12 h-12 rounded bg-white/5 flex items-center justify-center overflow-hidden">
                           <img
                             src={teamIcon}
                             alt={teamName}
                             className="w-full h-full object-cover"
                           />
                         </div>
                       )}
                       <span className="font-black text-lg text-white flex items-center gap-2 uppercase italic tracking-tighter">
                         <span className="text-slate-600 font-mono text-sm not-italic">
                            {`0${idx + 1}`}
                         </span> 
                         {teamName}
                       </span>
                     </div>
                     <span className="font-mono font-black text-lg text-white italic">{team.points} <span className="text-[10px] font-sans text-slate-500 font-bold not-italic">PTS</span></span>
                   </div>
                   <ProgressBar value={team.points} max={500} color="from-white to-slate-400 group-hover:from-blue-400 group-hover:to-cyan-400" height="h-2" />
                   <div className="absolute inset-0 opacity-10 mix-blend-overlay transition-opacity duration-500 group-hover:opacity-30" style={{backgroundColor: (team as any).color || '#fff'}}></div>
                 </div>
               );
             })}
          </div>
      </Card>
    </div>
  );
}

const HistoryView = ({ driverStandings, constructorStandings }: { driverStandings: DriverStanding[]; constructorStandings: ConstructorStanding[] }) => {
  const seasonKeys = useMemo(
    () => Object.keys(SEASONS_DATA).map((y) => Number(y)).sort((a, b) => a - b),
    []
  );
  const defaultSeason = seasonKeys[seasonKeys.length - 1] || 2024;
  const [activeSeason, setActiveSeason] = useState<number>(defaultSeason);
  const [selectedTeam, setSelectedTeam] = useState<any | null>(null);

  // Build season data from immutable archive, overlaying live standings when available
  const seasonData = useMemo(() => {
    const baseSeason = SEASONS_DATA[activeSeason];
    if (!baseSeason) return null;

    const liveConstructors = constructorStandings.filter(
      (c: any) => (c as any).season === undefined || (c as any).season === activeSeason
    );
    const liveDrivers = driverStandings.filter(
      (d: any) => (d as any).season === undefined || (d as any).season === activeSeason
    );

    const mergedTeams = baseSeason.teams.map((team) => {
      const liveTeam = liveConstructors.find(
        (c) => c.team_name.toLowerCase() === team.name.toLowerCase()
      );
      const points = liveTeam?.points ?? team.points;
      const rank = liveTeam?.position ?? team.rank;

      const drivers = team.drivers.map((d) => {
        const liveDriver = liveDrivers.find(
          (ld) => ld.driver_name.toLowerCase() === d.name.toLowerCase()
        );
        return {
          ...d,
          points: liveDriver?.points ?? d.points,
          wins: liveDriver?.wins ?? d.wins,
          podiums: liveDriver?.podiums ?? d.podiums,
        };
      });

      const extraDrivers = liveDrivers
        .filter((ld) => ld.team_name.toLowerCase() === team.name.toLowerCase())
        .filter((ld) => !drivers.find((d) => d.name.toLowerCase() === ld.driver_name.toLowerCase()))
        .map((ld) => {
          const visual = findDriverVisual(ld.driver_code, ld.driver_name, ld.team_name);
          return {
            name: ld.driver_name,
            points: ld.points,
            wins: ld.wins,
            podiums: ld.podiums,
            image: visual?.image || '',
          };
        });

      return {
        ...team,
        points,
        rank,
        drivers: [...drivers, ...extraDrivers],
        history: team.history,
      };
    });

    return { ...baseSeason, teams: mergedTeams };
  }, [activeSeason, constructorStandings, driverStandings]);

  // Champion driver for hero
  const championDriver = useMemo(() => {
    if (!seasonData) return null;
    const allDrivers = seasonData.teams.flatMap((t: any) =>
      (t.drivers || []).map((d: any) => ({ ...d, teamName: t.name, color: t.color }))
    );
    const top = allDrivers.slice().sort((a: any, b: any) => (b.points || 0) - (a.points || 0))[0];
    return top || null;
  }, [seasonData]);

  const leaderPoints = seasonData ? Math.max(...seasonData.teams.map((t: any) => t.points || 0), 1) : 1;

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-200 font-sans selection:bg-white/20">
      <div className="fixed inset-0 z-0 opacity-20 pointer-events-none" 
           style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px)', backgroundSize: '40px 40px' }}
      />

      <div className="relative z-10 p-6 md:p-12 max-w-[1800px] mx-auto">
        <header className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-8 border-b border-white/10 pb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="h-2 w-2 rounded-full bg-green-500 shadow-[0_0_10px_#22c55e]" />
              <span className="text-xs font-bold uppercase tracking-[0.2em] text-neutral-500">
                Archive Access
              </span>
            </div>
            <h1 className="text-6xl md:text-8xl font-black italic tracking-tighter text-white">
              HISTORY
            </h1>
          </div>

          <div className="flex flex-col items-end gap-2">
            <span className="text-xs font-bold uppercase tracking-widest text-neutral-500">Select Season</span>
            <div className="flex flex-wrap justify-end gap-2 max-w-xl">
              {seasonKeys.map((year) => (
                <button
                  key={year}
                  onClick={() => setActiveSeason(year)}
                  className={`px-3 py-1 text-sm font-bold rounded transition-all duration-300 border border-transparent ${
                    activeSeason === year
                      ? 'bg-white text-black border-white'
                      : 'bg-neutral-900 text-neutral-500 border-white/10 hover:border-white/50 hover:text-white'
                  }`}
                >
                  {year}
                </button>
              ))}
            </div>
          </div>
        </header>

        <div className="flex flex-col lg:flex-row gap-8">
          {seasonData && championDriver && (
            <motion.div 
              key={`hero-${activeSeason}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="w-full lg:w-[25%] relative group flex flex-col gap-4"
            >
              <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-[#0a0a0a] h-[500px]">
                <div
                  className="absolute inset-0 z-0 opacity-40 transition-colors duration-700"
                  style={{ background: `linear-gradient(180deg, ${championDriver.color || seasonData.championColor} 0%, transparent 100%)` }}
                />
                <div className="relative z-10 p-6 h-full flex flex-col">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-white/60 mb-1 block">
                        Champion
                      </span>
                      <h2 className="text-4xl font-black italic uppercase text-white leading-none">
                        {championDriver.name?.split(' ').slice(-1)[0]}
                      </h2>
                      <p className="text-sm text-white/80 font-bold mt-1">{championDriver.teamName}</p>
                    </div>
                    <Award className="w-8 h-8 text-white opacity-80" />
                  </div>
                  <div className="flex-1 relative mt-4">
                    <img
                      src={championDriver.image}
                      alt="Champion"
                      className="w-full h-full object-contain object-bottom drop-shadow-2xl scale-100 origin-bottom transition-transform duration-500 group-hover:scale-105"
                    />
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-1 gap-2">
                <div className="bg-[#0f0f0f] border border-white/5 p-4 rounded-xl flex justify-between items-center">
                  <span className="text-xs uppercase font-bold text-neutral-500">Season Pts</span>
                  <span className="text-2xl font-mono font-bold text-white">{championDriver?.points || '—'}</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-[#0f0f0f] border border-white/5 p-4 rounded-xl">
                    <span className="text-[10px] uppercase font-bold text-neutral-500 block mb-1">Wins</span>
                    <span className="text-xl font-bold text-white">{championDriver?.wins || '—'}</span>
                  </div>
                  <div className="bg-[#0f0f0f] border border-white/5 p-4 rounded-xl">
                    <span className="text-[10px] uppercase font-bold text-neutral-500 block mb-1">Podiums</span>
                    <span className="text-xl font-bold text-white">{championDriver?.podiums || '—'}</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          <div className="w-full lg:w-[75%] grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 auto-rows-min">
            {seasonData?.teams.map((team: any, idx: number) => (
              <motion.div
                key={team.id || `${team.name}-${idx}`}
                layoutId={`card-${team.id || team.name}-${activeSeason}`}
                onClick={() => setSelectedTeam(team)}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="relative h-60 cursor-pointer overflow-hidden rounded-xl bg-[#0a0a0a] border border-white/5 hover:border-white/20 transition-all group hover:shadow-2xl"
              >
                <div
                  className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-500"
                  style={{ background: `radial-gradient(circle at center, ${team.color}, transparent)` }}
                />
                <div className="relative z-10 p-5 flex flex-col h-full justify-between">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-black uppercase italic tracking-tight text-white">{team.name}</span>
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="h-1.5 w-1.5 rounded-full" style={{ background: team.color }} />
                        <span className="text-[10px] font-bold text-neutral-400 uppercase">Rank #{team.rank}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-white tabular-nums">
                        {team.points} <span className="text-[10px] text-neutral-600">PTS</span>
                      </div>
                    </div>
                  </div>

                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none mt-2">
                    <img
                      src={team.carImage}
                      className="w-[90%] object-contain drop-shadow-2xl transition-transform duration-500 group-hover:scale-110 group-hover:-translate-y-2"
                    />
                  </div>

                  <div className="relative z-20 mt-4">
                    <div className="text-[10px] uppercase font-bold text-neutral-500 mb-1">Season Trajectory</div>
                    <div className="flex items-end gap-1 h-16">
                      {buildTrajectory(team).map((pts: number, i: number, arr: number[]) => {
                        const maxHist = Math.max(...arr, 1);
                        const h = Math.max(6, (pts / maxHist) * 100);
                        return (
                          <div key={i} className="flex-1">
                            <div
                              className="w-full rounded-sm bg-neutral-800/70"
                              style={{ height: `${h}%` }}
                            >
                              <div
                                className="w-full h-full rounded-sm"
                                style={{ background: `${team.color}CC` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <div className="mt-auto pt-4 relative z-20 flex justify-between items-end">
                    <div className="flex -space-x-2">
                      {(team.drivers || []).slice(0, 2).map((d: any, i: number) => (
                        <img
                          key={i}
                          src={d.image}
                          className="w-6 h-6 rounded-full border border-[#0a0a0a] bg-neutral-800 object-cover"
                          title={d.name}
                        />
                      ))}
                    </div>
                    <div className="w-16 h-1 bg-neutral-800 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full"
                        style={{ width: `${Math.min(100, (team.points / leaderPoints) * 100)}%`, background: team.color }}
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center text-xs text-neutral-600 font-mono">
          <div className="flex items-center gap-2">
            <span className="bg-red-600 text-black font-bold px-1 rounded">ADMIN</span>
            <span>ENGINEER ACCESS ONLY</span>
          </div>
          <div>F1 HISTORICAL ARCHIVE // 2018-2025</div>
        </div>
      </div>

      <AnimatePresence>
        {selectedTeam && <TelemetryDrawer team={selectedTeam} onClose={() => setSelectedTeam(null)} />}
      </AnimatePresence>
    </div>
  );
};

const RaceExplorerView = ({ activeRace, raceWeather, raceResults, sessionResults, sessions, onSessionChange, selectedSessionType }: { activeRace: Race, raceWeather: WeatherSummary, raceResults: SessionResultRow[], sessionResults: SessionResultRow[], sessions: SessionMeta[], onSessionChange: (code: string) => void, selectedSessionType: string }) => {
  const resultsSorted = raceResults
    .slice()
    .sort((a, b) => (a.position || 99) - (b.position || 99));

  const podium = resultsSorted.slice(0, 3);
  const winner = resultsSorted[0] || null;

  const gridTop = resultsSorted
    .filter((r) => r.grid !== null && r.grid !== undefined)
    .sort((a, b) => (a.grid || 99) - (b.grid || 99))
    .slice(0, 5);

  const sessionSorted = sessionResults
    .slice()
    .sort((a, b) => (a.position || 99) - (b.position || 99));
  const derivedLaps = raceResults.reduce((max, r) => Math.max(max, r.laps ?? 0), 0);
  const raceLapsDisplay = derivedLaps || activeRace.laps || 0;
  const displayRain = raceWeather.rain ?? raceWeather.humidity ?? activeRace.rainProb ?? 0;

  // Filter sessions based on season: 2023-2025 show all (FP1, FP2, FP3, Q, R), 2018-2022 show only Q, R
  const season = activeRace.season || new Date().getFullYear();
  const filteredSessions = season >= 2023 
    ? sessions
    : sessions.filter(s => ['Q', 'R'].includes(s.session_type));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-in fade-in duration-500">
      <div className="lg:col-span-8 space-y-6">
        <Card title="Race Summary" className="!border-white/10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="text-[10px] uppercase font-black text-slate-500 tracking-widest">Winner</div>
              <div className="bg-white/5 border border-white/10 rounded-sm p-3 flex items-center justify-between">
                <div className="text-white font-black uppercase italic tracking-wider">{winner?.driver_name || winner?.driver_code || 'N/A'}</div>
                <div className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">{winner?.team_name || ''}</div>
              </div>
              <div className="text-[10px] uppercase font-black text-slate-500 tracking-widest">Weather</div>
              <div className="bg-white/5 border border-white/10 rounded-sm p-3 flex items-center justify-between">
                <span className="text-slate-300 font-bold flex items-center gap-2"><Droplets size={14} className="text-blue-400" /> Rain</span>
                <span className="text-white font-mono font-black italic">{displayRain !== null && displayRain !== undefined ? `${Number(displayRain).toFixed(0)}%` : '—'}</span>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-sm p-3 flex items-center justify-between">
                <span className="text-slate-300 font-bold flex items-center gap-2"><Thermometer size={14} className="text-orange-400" /> Track Temp</span>
                <span className="text-white font-mono font-black italic">{raceWeather.trackTemp !== null && raceWeather.trackTemp !== undefined ? `${raceWeather.trackTemp.toFixed(1)}°C` : '—'}</span>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-sm p-3 flex items-center justify-between">
                <span className="text-slate-300 font-bold flex items-center gap-2"><Flag size={14} className="text-green-400" /> Laps</span>
                <span className="text-white font-mono font-black italic">{raceLapsDisplay || '—'}</span>
              </div>
            </div>
            <div className="space-y-3">
              <div className="text-[10px] uppercase font-black text-slate-500 tracking-widest">Podium</div>
              <div className="space-y-2">
                {podium.map((p, idx) => (
                  <div key={`${p.driver_code}-${idx}`} className="flex items-center justify-between bg-white/5 border border-white/10 rounded-sm px-3 py-2">
                    <div className="flex items-center gap-2">
                      <span className="text-slate-500 font-mono text-xs">P{p.position ?? idx + 1}</span>
                      <span className="text-white font-black uppercase italic tracking-wider">{p.driver_name || p.driver_code}</span>
                    </div>
                    <span className="text-white font-mono font-black italic">{p.gap || p.status || '—'}</span>
                  </div>
                ))}
                {!podium.length && <div className="text-slate-500 text-xs font-bold uppercase tracking-widest">No podium data</div>}
              </div>
              <div className="text-[10px] uppercase font-black text-slate-500 tracking-widest mt-3">Starting Grid (Top 5)</div>
              <div className="space-y-1">
                {gridTop.map((p, idx) => (
                  <div key={`${p.driver_code}-grid-${idx}`} className="flex justify-between text-sm bg-white/5 border border-white/10 rounded-sm px-3 py-1">
                    <span className="text-white font-bold italic">P{p.grid}</span>
                    <span className="text-slate-300 font-bold">{p.driver_name || p.driver_code}</span>
                  </div>
                ))}
                {!gridTop.length && <div className="text-slate-500 text-[11px] font-bold uppercase tracking-widest">No grid data</div>}
              </div>
            </div>
          </div>
        </Card>
        <Card title="Race Results" className="!border-white/10">
          <div className="flex justify-between text-[10px] uppercase font-black text-slate-500 tracking-widest mb-3">
            <span>{activeRace.name}</span>
            <span>Round {activeRace.round}</span>
          </div>
          <div className="space-y-2 max-h-80 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10">
            {(resultsSorted.length ? resultsSorted : podium).map((p, idx) => (
              <div key={`${p.driver_code}-${idx}`} className="flex items-center justify-between bg-white/5 px-3 py-2 rounded-sm border border-white/5">
                <div className="flex items-center gap-3">
                  <span className="text-slate-500 font-mono text-xs">P{p.position ?? idx + 1}</span>
                  <span className="text-white font-black uppercase tracking-wider italic text-sm">{p.driver_name || p.driver_code}</span>
                  <Badge color="neutral">{p.team_name || 'Team'}</Badge>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-slate-400 text-[10px] uppercase font-black">{p.status || 'Time'}</span>
                  <span className="text-white font-mono font-black italic text-lg">{p.time_or_duration || p.gap || '—'}</span>
                </div>
              </div>
            ))}
            {!resultsSorted.length && !podium.length && (
              <div className="text-slate-500 text-xs font-bold uppercase tracking-widest text-center py-4">No data for this race</div>
            )}
          </div>
        </Card>
      </div>

      <div className="lg:col-span-4 space-y-6">
        <Card title="Sessions" className="!border-blue-500/20">
          <div className="flex flex-wrap gap-2 mb-4">
            {filteredSessions.map((s) => (
              <button
                key={s.session_key}
                onClick={() => onSessionChange(s.session_type)}
                className={`px-4 py-2 text-xs font-black uppercase tracking-wider rounded-sm border skew-x-[-10deg] ${s.session_type === 'R' ? 'hover:border-red-500 hover:text-white' : 'hover:border-white/30 hover:text-white'} ${selectedSessionType === s.session_type ? 'bg-white text-black border-white shadow-[0_0_15px_rgba(255,255,255,0.3)]' : 'bg-slate-900/50 text-slate-400 border-white/10'}`}
              >
                <span className="skew-x-[10deg] block">{s.session_type}</span>
              </button>
            ))}
          </div>
          <div className="space-y-2 max-h-80 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10">
            {sessionSorted.map((p, idx) => (
              <div key={`${p.driver_code}-${idx}`} className="flex items-center justify-between bg-white/5 px-3 py-2 rounded-sm border border-white/5">
                <div className="flex items-center gap-3">
                  <span className="text-slate-500 font-mono text-xs">P{p.position ?? idx + 1}</span>
                  <span className="text-white font-black uppercase tracking-wider italic text-sm">{p.driver_name || p.driver_code}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-slate-400 text-[10px] uppercase font-black">{p.status || 'Time'}</span>
                  <span className="text-white font-mono font-black italic text-lg">{p.time_or_duration || p.gap || '—'}</span>
                </div>
              </div>
            ))}
            {!sessionSorted.length && <div className="text-slate-500 text-xs font-bold uppercase tracking-widest text-center py-4">No session data</div>}
          </div>
        </Card>
      </div>
    </div>
  );
}

const StrategyView = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in duration-500">
      {/* Skill Overview / Tech Stack */}
      <div className="lg:col-span-8 space-y-6">
        <Card title="Data Engineering Skillset" className="!border-purple-500/20" actionIcon={<TrendingUp size={16} className="text-purple-400" />}>
          <div className="grid md:grid-cols-3 gap-4 text-xs uppercase tracking-widest text-slate-400 font-black">
            <div className="space-y-2">
              <div className="text-[10px] text-slate-500">INGESTION</div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span>Streaming APIs</span>
                  <Badge color="green">OpenF1</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Batch Pipelines</span>
                  <Badge color="green">Python</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>File Lakes</span>
                  <Badge color="cyan">Parquet</Badge>
                </div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-[10px] text-slate-500">WAREHOUSE & MODELING</div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span>Lakehouse</span>
                  <Badge color="green">DuckDB</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Transformations</span>
                  <Badge color="yellow">dbt</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Dimensional Design</span>
                  <Badge color="cyan">Star/Snowflake</Badge>
                </div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-[10px] text-slate-500">ML & SERVING</div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span>Modeling</span>
                  <Badge color="blue">Random Forest</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Feature Store</span>
                  <Badge color="blue">Feature Views</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>APIs</span>
                  <Badge color="green">FastAPI</Badge>
                </div>
              </div>
            </div>
          </div>
        </Card>

        <Card title="Project Highlights" className="!border-cyan-500/20">
          <div className="grid md:grid-cols-3 gap-4 text-xs font-mono text-slate-300">
            <div className="bg-white/5 p-4 rounded-sm border border-white/10">
              <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-2">OpenF1 Bronze Layer</div>
              <div className="text-3xl font-black text-white italic mb-1">2023–2024</div>
              <p className="text-[11px] leading-relaxed">External Parquet lake wired into DuckDB with partitioned sessions, session_result, drivers, starting_grid and weather for two full seasons.</p>
            </div>
            <div className="bg-white/5 p-4 rounded-sm border border-white/10">
              <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-2">Prediction Service</div>
              <div className="text-3xl font-black text-white italic mb-1">Race Predictor</div>
              <p className="text-[11px] leading-relaxed">
                Random Forest model trained on 2022‑2024 F1 results with qualifying position, driver/ team form,
                circuit‑specific performance and 2025 lineup changes (e.g. Hamilton → Ferrari), served via FastAPI.
              </p>
            </div>
            <div className="bg-white/5 p-4 rounded-sm border border-white/10">
              <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-2">Analytics UI</div>
              <div className="text-3xl font-black text-white italic mb-1">OpenF1 Pitwall</div>
              <p className="text-[11px] leading-relaxed">React + Tailwind dashboard wired to bronze + predictions, including standings, race explorer, model lab, and DE monitor views.</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Tooling / Portfolio widgets */}
      <div className="lg:col-span-4 space-y-8">
        <Card title="Toolbox" className="!border-green-500/20" actionIcon={<Database size={16} className="text-green-400" />}>
          <div className="grid grid-cols-2 gap-3 text-[11px] font-mono text-slate-300">
            <div className="bg-black/40 border border-white/10 rounded-sm p-3">
              <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Storage</div>
              <ul className="space-y-1">
                <li>• DuckDB / Parquet</li>
                <li>• S3‑style object lakes</li>
                <li>• Local lakehouse dev</li>
              </ul>
            </div>
            <div className="bg-black/40 border border-white/10 rounded-sm p-3">
              <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Processing</div>
              <ul className="space-y-1">
                <li>• Python / Pandas</li>
                <li>• dbt Core models</li>
                <li>• Orchestrated batch jobs</li>
              </ul>
            </div>
            <div className="bg-black/40 border border-white/10 rounded-sm p-3">
              <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">ML / Analytics</div>
              <ul className="space-y-1">
                <li>• XGBoost, scikit‑learn</li>
                <li>• Feature engineering</li>
                <li>• Model monitoring</li>
              </ul>
            </div>
            <div className="bg-black/40 border border-white/10 rounded-sm p-3">
              <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Ops</div>
              <ul className="space-y-1">
                <li>• Dockerized services</li>
                <li>• FastAPI backends</li>
                <li>• CI‑ready project layout</li>
              </ul>
            </div>
          </div>
        </Card>

        <Card title="Narrative" className="!border-blue-500/20" actionIcon={<Code size={16} className="text-blue-400" />}>
          <p className="text-[11px] text-slate-300 leading-relaxed font-mono">
            This Strategy tab doubles as a data engineering portfolio: starting from raw OpenF1 telemetry,
            data is ingested into a bronze lake, modelled into analytics‑ready views with DuckDB + dbt,
            and surfaced through FastAPI into this React dashboard. The same patterns apply to any
            event‑driven analytics workload: build a clean lakehouse, design reliable pipelines, and
            expose fast, well‑typed APIs for downstream consumers.
          </p>
        </Card>
      </div>
    </div>
  );
}

const PredictionsLab = ({ season, round }: { season: number | null, round: number | null }) => {
  const [rainProb, setRainProb] = useState(0);
  const [humidity, setHumidity] = useState(50);
  const [temperature, setTemperature] = useState(20);
  const [isSimulating, setIsSimulating] = useState(false);
  const [selectedDriver, setSelectedDriver] = useState<string | null>(null);
  const [gridPos, setGridPos] = useState(10);
  const [tireType, setTireType] = useState<'Soft' | 'Medium' | 'Hard' | 'Intermediate' | 'Wet'>('Soft');
  const [scenarioProb, setScenarioProb] = useState<number | null>(null);
  const [selectedRaceKey, setSelectedRaceKey] = useState<string | null>(null);
  const [raceDropdownOpen, setRaceDropdownOpen] = useState(false);
  const [driverDropdownOpen, setDriverDropdownOpen] = useState(false);
  const [availableRaces, setAvailableRaces] = useState<{season: number, round: number, name: string}[]>([]);
  const [driversByRace, setDriversByRace] = useState<Record<string, {code: string, name: string}[]>>({});

  // Load race and driver data from static JSON
  useEffect(() => {
    fetch('/race-data.json')
      .then(res => res.json())
      .then(data => {
        setAvailableRaces(data.races || []);
        setDriversByRace(data.driversByRace || {});
      })
      .catch(err => {
        console.error('Failed to load race data:', err);
      });
  }, []);

  // Get the current race key from state or use first available race
  const currentRaceKey = useMemo(() => {
    return selectedRaceKey || (availableRaces.length > 0 ? `${availableRaces[0].season}-${availableRaces[0].round}` : null);
  }, [selectedRaceKey, availableRaces]);
  
  // Parse selected race
  const selectedRaceData = useMemo(() => {
    if (!currentRaceKey) return null;
    const [s, r] = currentRaceKey.split('-').map(Number);
    return { season: s, round: r };
  }, [currentRaceKey]);

  // Close dropdowns on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setRaceDropdownOpen(false);
        setDriverDropdownOpen(false);
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  // Get driver options from static data for selected race
  const driverOptions = useMemo(() => {
    if (!currentRaceKey || !driversByRace[currentRaceKey]) return [];
    return driversByRace[currentRaceKey].map(d => ({
      season: selectedRaceData?.season || 0,
      round: selectedRaceData?.round || 0,
      driver_code: d.code,
      driver_name: d.name,
      team_name: null,
      pred_win_proba: 0,
      pred_win_proba_softmax: 0,
      grid_position: null,
    }));
  }, [currentRaceKey, driversByRace, selectedRaceData]);

  useEffect(() => {
    if (driverOptions.length) {
      const first = driverOptions[0];
      setSelectedDriver(first.driver_code || first.driver_name || null);
      const gridFromPrediction = first.grid_position ?? 10;
      setGridPos(Math.max(1, Math.min(20, gridFromPrediction)));
    }
  }, [driverOptions, season, round]);

  const selectedPrediction = useMemo(() => {
    if (!selectedDriver) return null;
    return driverOptions.find(p => p.driver_code === selectedDriver) || null;
  }, [driverOptions, selectedDriver]);

  const selectedRaceDisplay = useMemo(() => {
    if (!currentRaceKey) return 'Select Race...';
    const race = availableRaces.find(r => `${r.season}-${r.round}` === currentRaceKey);
    if (!race) return 'Select Race...';
    return race.name;
  }, [currentRaceKey, availableRaces]);

  const selectedDriverDisplay = useMemo(() => {
    if (!selectedDriver) return 'Select Driver';
    const driver = driverOptions.find(d => d.driver_code === selectedDriver);
    if (!driver) return 'Select Driver';
    return driver.driver_name || driver.driver_code || 'Unknown';
  }, [selectedDriver, driverOptions]);

  const baseProb = selectedPrediction
    ? (selectedPrediction.pred_win_proba_softmax ?? selectedPrediction.pred_win_proba ?? 0)
    : 0;

  const effectiveProb = scenarioProb ?? baseProb;

  const mapTyreToIndex = (t: typeof tireType): number => {
    switch (t) {
      case 'Soft':
        return 3;
      case 'Medium':
        return 2;
      case 'Hard':
        return 1;
      case 'Intermediate':
        return 4;
      case 'Wet':
        return 5;
      default:
        return 3;
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in duration-500">
      <div className="lg:col-span-5 space-y-8">
        <Card title="Predictor Controls" className="h-full !border-purple-500/20" actionIcon={<Settings size={16} className="text-purple-400" />}>
           <div className="space-y-6 py-4">
             {/* Race Selector */}
             <div>
               <label className="text-xs font-black uppercase tracking-wider text-slate-400 mb-2 block">Select Race</label>
               <div className="relative" onClick={(e) => e.stopPropagation()}>
                 <button
                   onClick={(e) => {
                     e.stopPropagation();
                     setRaceDropdownOpen(!raceDropdownOpen);
                   }}
                   className="w-full bg-slate-900/60 border border-white/10 text-white text-sm font-bold rounded-sm px-3 py-2 outline-none hover:border-purple-500/30 focus:border-purple-500/50 transition-colors text-left flex justify-between items-center"
                 >
                   <span>{selectedRaceDisplay}</span>
                   <ChevronDown size={14} className={`transition-transform ${raceDropdownOpen ? 'rotate-180' : ''}`} />
                 </button>
                 {raceDropdownOpen && (
                   <div className="absolute z-50 w-full mt-1 bg-slate-950 border border-white/10 rounded-sm shadow-lg max-h-48 overflow-y-auto">
                     {availableRaces.length === 0 ? (
                       <div className="px-3 py-2 text-sm text-slate-400">No races available</div>
                     ) : (
                       availableRaces.map((r) => (
                         <button
                           key={`${r.season}-${r.round}`}
                           onClick={(e) => {
                             e.stopPropagation();
                             setSelectedRaceKey(`${r.season}-${r.round}`);
                             setRaceDropdownOpen(false);
                           }}
                           className={`w-full text-left px-3 py-2 text-sm hover:bg-purple-500/20 transition-colors ${
                             currentRaceKey === `${r.season}-${r.round}` ? 'bg-purple-500/30 text-purple-300' : 'text-white'
                           }`}
                         >
                           {r.name}
                         </button>
                       ))
                     )}
                   </div>
                 )}
               </div>
             </div>

             {/* Driver Selector */}
             <div>
               <label className="text-xs font-black uppercase tracking-wider text-slate-400 mb-2 block">Driver</label>
               <div className="relative" onClick={(e) => e.stopPropagation()}>
                 <button
                   onClick={(e) => {
                     e.stopPropagation();
                     setDriverDropdownOpen(!driverDropdownOpen);
                   }}
                   className="w-full bg-slate-900/60 border border-white/10 text-white text-sm font-bold rounded-sm px-3 py-2 outline-none hover:border-purple-500/30 focus:border-purple-500/50 transition-colors text-left flex justify-between items-center"
                 >
                   <span>{selectedDriverDisplay}</span>
                   <ChevronDown size={14} className={`transition-transform ${driverDropdownOpen ? 'rotate-180' : ''}`} />
                 </button>
                 {driverDropdownOpen && (
                   <div className="absolute z-50 w-full mt-1 bg-slate-950 border border-white/10 rounded-sm shadow-lg max-h-48 overflow-y-auto">
                     {driverOptions.length === 0 ? (
                       <div className="px-3 py-2 text-sm text-slate-400">Select a race first</div>
                     ) : (
                       driverOptions.map((p) => (
                         <button
                           key={p.driver_code || p.driver_name}
                           onClick={(e) => {
                             e.stopPropagation();
                             setSelectedDriver(p.driver_code || null);
                             setDriverDropdownOpen(false);
                           }}
                           className={`w-full text-left px-3 py-2 text-sm hover:bg-purple-500/20 transition-colors ${
                             selectedDriver === p.driver_code ? 'bg-purple-500/30 text-purple-300' : 'text-white'
                           }`}
                         >
                           {p.driver_name || p.driver_code}
                         </button>
                       ))
                     )}
                   </div>
                 )}
               </div>
             </div>

             {/* Weather Sliders */}
             <div className="pt-2">
               <div className="flex justify-between items-center mb-3">
                 <label className="text-xs font-black uppercase tracking-wider text-slate-400">Weather Conditions</label>
                 <div className="text-[10px] text-slate-500">Interactive Scenario</div>
               </div>
               
               {/* Rain */}
               <div className="mb-4">
                 <div className="flex justify-between text-xs mb-2">
                   <span className="text-slate-400 font-bold">Rainfall</span>
                   <span className="text-cyan-400 font-black">{rainProb}%</span>
                 </div>
                 <div className="relative h-2 bg-slate-800 rounded-sm">
                    <div className="absolute h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-sm transition-all" style={{width: `${rainProb}%`}}></div>
                    <input type="range" min="0" max="100" value={rainProb} onChange={(e) => setRainProb(Number(e.target.value))} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"/>
                    <div className="absolute top-1/2 -translate-y-1/2 w-3 h-5 bg-white border-2 border-slate-900 rounded shadow-[0_0_8px_rgba(34,211,238,0.8)] pointer-events-none transition-all" style={{left: `calc(${rainProb}% - 6px)`}}></div>
                 </div>
               </div>

               {/* Humidity */}
               <div className="mb-4">
                 <div className="flex justify-between text-xs mb-2">
                   <span className="text-slate-400 font-bold">Humidity</span>
                   <span className="text-blue-400 font-black">{humidity}%</span>
                 </div>
                 <div className="relative h-2 bg-slate-800 rounded-sm">
                    <div className="absolute h-full bg-gradient-to-r from-blue-600 to-blue-400 rounded-sm transition-all" style={{width: `${humidity}%`}}></div>
                    <input type="range" min="0" max="100" value={humidity} onChange={(e) => setHumidity(Number(e.target.value))} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"/>
                    <div className="absolute top-1/2 -translate-y-1/2 w-3 h-5 bg-white border-2 border-slate-900 rounded shadow-[0_0_8px_rgba(59,130,246,0.8)] pointer-events-none transition-all" style={{left: `calc(${humidity}% - 6px)`}}></div>
                 </div>
               </div>

               {/* Temperature */}
               <div className="mb-4">
                 <div className="flex justify-between text-xs mb-2">
                   <span className="text-slate-400 font-bold">Temperature (°C)</span>
                   <span className="text-orange-400 font-black">{temperature}°</span>
                 </div>
                 <div className="relative h-2 bg-slate-800 rounded-sm">
                    <div className="absolute h-full bg-gradient-to-r from-orange-600 to-red-500 rounded-sm transition-all" style={{width: `${((temperature + 10) / 40) * 100}%`}}></div>
                    <input type="range" min="-10" max="30" value={temperature} onChange={(e) => setTemperature(Number(e.target.value))} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"/>
                    <div className="absolute top-1/2 -translate-y-1/2 w-3 h-5 bg-white border-2 border-slate-900 rounded shadow-[0_0_8px_rgba(239,68,68,0.8)] pointer-events-none transition-all" style={{left: `calc(${((temperature + 10) / 40) * 100}% - 6px)`}}></div>
                 </div>
               </div>
             </div>
             
             {/* Grid Position */}
             <div>
               <div className="flex justify-between text-xs mb-3">
                 <span className="text-slate-400 font-black uppercase tracking-wider">Starting Grid Position</span>
                 <span className="text-red-400 text-base font-black italic">P{gridPos}</span>
               </div>
               <div className="relative h-2 bg-slate-800 rounded-sm">
                  <div className="absolute h-full bg-gradient-to-r from-red-600 to-orange-500 rounded-sm transition-all" style={{width: `${(gridPos/20)*100}%`}}></div>
                  <input
                    type="range"
                    min="1"
                    max="20"
                    step="1"
                    value={gridPos}
                    onChange={(e) => setGridPos(Number(e.target.value))}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer pointer-events-auto"
                  />
                  <div className="absolute top-1/2 -translate-y-1/2 w-3 h-5 bg-white border-2 border-slate-900 rounded shadow-[0_0_8px_rgba(239,68,68,0.8)] pointer-events-none transition-all" style={{left: `calc(${(gridPos/20)*100}% - 6px)`}}></div>
               </div>
               <div className="flex justify-between text-[9px] text-slate-600 mt-2 font-black uppercase tracking-widest"><span>Front</span><span>Back</span></div>
             </div>

             {/* Tire Compound */}
             <div>
               <label className="text-xs font-black uppercase tracking-wider text-slate-400 mb-2 block">Tyre Compound</label>
               <select
                 value={tireType}
                 onChange={(e) => setTireType(e.target.value as any)}
                 className="w-full bg-slate-900/60 border border-white/10 text-white text-sm font-bold rounded-sm px-3 py-2 outline-none hover:border-purple-500/30 focus:border-purple-500/50 transition-colors"
               >
                 <option value="Soft">Soft (C5-C3)</option>
                 <option value="Medium">Medium (C4-C2)</option>
                 <option value="Hard">Hard (C3-C1)</option>
                 <option value="Intermediate">Intermediate</option>
                 <option value="Wet">Wet</option>
               </select>
             </div>

             {/* Prediction Button */}
             <button 
              onClick={async () => {
                if (!selectedPrediction || !selectedRaceData) {
                  alert('Please select a race and driver');
                  return;
                }
                setIsSimulating(true);
                try {
                  const driverCode = selectedPrediction.driver_code || selectedPrediction.driver_name || '';
                  const body = {
                    season: selectedRaceData.season,
                    round: selectedRaceData.round,
                    driver_code: driverCode,
                    grid_position: gridPos,
                    rain_probability: rainProb / 100,
                    starting_compound_index: mapTyreToIndex(tireType),
                  };
                  const res = await fetch(`${API_BASE_URL}/api/predict/race_win_scenario`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body),
                  });
                  if (res.ok) {
                    const data = await res.json();
                    if (typeof data.scenario_pred_win_proba === 'number') {
                      setScenarioProb(data.scenario_pred_win_proba);
                    } else {
                      setScenarioProb(null);
                    }
                  } else {
                    setScenarioProb(null);
                  }
                } catch (err) {
                  console.error('Prediction error:', err);
                  setScenarioProb(null);
                } finally {
                  setIsSimulating(false);
                }
              }}
              disabled={isSimulating || !selectedDriver || !currentRaceKey}
              className={`w-full mt-6 bg-gradient-to-r from-purple-600 to-purple-500 text-white font-black py-3 rounded-sm hover:from-purple-500 hover:to-purple-400 transition-all flex justify-center items-center gap-3 text-sm tracking-[0.15em] uppercase disabled:opacity-50 disabled:cursor-not-allowed ${isSimulating ? 'opacity-80' : 'hover:shadow-[0_0_20px_rgba(168,85,247,0.4)]'}`}
             >
               <span className="flex items-center gap-2">
                  {isSimulating ? <PlayCircle size={18} className="animate-spin" /> : <Zap size={18} />}
                  {isSimulating ? 'Predicting...' : 'Get Prediction'}
               </span>
             </button>
           </div>
        </Card>
      </div>

      <div className="lg:col-span-7">
        <Card title="Win Probability" className="h-full !border-green-500/20" actionIcon={<TrendingUp size={16} className="text-green-400" />}>
           <div className="flex items-center justify-center h-full min-h-[500px] py-6 relative z-10">
             {/* Model probability for the selected driver */}
             {selectedPrediction && currentRaceKey ? (
               <div className="w-full space-y-8">
                 {/* Driver Header with Probability */}
                 <div className="flex justify-between items-center mb-6 pb-4 border-b border-white/10">
                   <div>
                     <div className="text-slate-500 text-xs font-black uppercase tracking-widest mb-1">Selected Driver</div>
                     <div className="text-white font-black text-2xl flex items-center gap-2">
                       <span>{selectedPrediction.driver_code}</span>
                       <span className="text-xs text-slate-400 font-normal">{selectedPrediction.team_name}</span>
                     </div>
                   </div>
                   <div className="text-right">
                     <div className="text-slate-500 text-xs font-black uppercase tracking-widest mb-1">Win Probability</div>
                     <div className="font-mono font-black text-4xl text-green-400 italic" style={{textShadow: '0 0 20px rgba(74,222,128,0.3)'}}>{isSimulating ? <span className="animate-pulse text-2xl">--</span> : `${(effectiveProb * 100).toFixed(1)}%`}</div>
                   </div>
                 </div>

                 {/* Progress Bar */}
                 <div className="space-y-2">
                   <div className="w-full h-8 bg-slate-900/60 border border-white/10 rounded-sm overflow-hidden relative backdrop-blur-md">
                     <div className="h-full bg-gradient-to-r from-green-600 via-green-500 to-emerald-400 transition-all duration-700 ease-out flex items-center justify-end pr-3" style={{width: isSimulating ? '0%' : `${effectiveProb * 100}%`}}>
                       {effectiveProb > 0.15 && (
                         <span className="text-white font-black text-xs tracking-wider drop-shadow-lg">{(effectiveProb * 100).toFixed(1)}%</span>
                       )}
                     </div>
                   </div>
                 </div>

                 {/* Scenario Details */}
                 <div className="grid grid-cols-2 gap-4 pt-4">
                   <div className="bg-white/5 border border-white/10 rounded-sm p-3">
                     <div className="text-[9px] text-slate-500 font-black uppercase tracking-widest mb-1">Base Probability</div>
                     <div className="text-lg font-black text-slate-300">{((selectedPrediction.pred_win_proba_softmax ?? selectedPrediction.pred_win_proba ?? 0) * 100).toFixed(1)}%</div>
                   </div>
                   <div className="bg-white/5 border border-white/10 rounded-sm p-3">
                     <div className="text-[9px] text-slate-500 font-black uppercase tracking-widest mb-1">Scenario Adjustment</div>
                     <div className={`text-lg font-black ${scenarioProb ? (scenarioProb > baseProb ? 'text-green-400' : 'text-red-400') : 'text-slate-300'}`}>
                       {scenarioProb ? `${((scenarioProb - baseProb) * 100).toFixed(1)}%` : 'Pending'}
                     </div>
                   </div>
                 </div>

                 {/* Scenario Configuration */}
                 <div className="mt-4 pt-4 border-t border-white/10">
                   <div className="text-xs font-black uppercase tracking-wider text-slate-400 mb-3">Current Scenario</div>
                   <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-300">
                     <div className="flex justify-between"><span className="text-slate-500">Grid Position:</span> <span className="text-white font-bold">P{gridPos}</span></div>
                     <div className="flex justify-between"><span className="text-slate-500">Rainfall:</span> <span className="text-cyan-400">{rainProb}%</span></div>
                     <div className="flex justify-between"><span className="text-slate-500">Humidity:</span> <span className="text-blue-400">{humidity}%</span></div>
                     <div className="flex justify-between"><span className="text-slate-500">Temperature:</span> <span className="text-orange-400">{temperature}°C</span></div>
                     <div className="flex justify-between col-span-2"><span className="text-slate-500">Tyre:</span> <span className="text-white font-bold">{tireType}</span></div>
                   </div>
                 </div>
               </div>
             ) : (
               <div className="text-center py-16">
                 <div className="text-slate-500 text-sm font-bold uppercase tracking-widest mb-2">Ready to Predict</div>
                 <div className="text-slate-600 text-xs">Select a race and driver from the controls panel</div>
               </div>
             )}
           </div>
        </Card>
      </div>
    </div>
  );
};

const PipelineView = ({ summary, monitor }: { summary?: PredictionSummary | null; monitor?: MonitorPayload | null }) => {
  const modelSummary = monitor?.model || summary || null;
  const hit1Pct = modelSummary ? (modelSummary.hit_at_1 * 100).toFixed(1) : '--';
  const hit3Pct = modelSummary ? (modelSummary.hit_at_3 * 100).toFixed(1) : '--';
  const bronze = monitor?.bronze;
  const latestSession = bronze?.latest_session;
  const predictionsInfo = monitor?.predictions;
  const latestSessionLabel = latestSession
    ? `${latestSession.season} · R${latestSession.round} · ${latestSession.grand_prix_slug || ''}`
    : 'No sessions found';
  return (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 animate-in fade-in duration-500">
    <Card title="Ingestion" className="!border-green-500/20" actionIcon={<Database size={16} className="text-green-400" />}>
      <div className="flex items-center gap-6 mb-6">
        <div className="p-4 bg-green-500/10 rounded-sm border border-green-500/20 shadow-[0_0_20px_rgba(34,197,94,0.2)]"><Database className="text-green-400" size={32} /></div>
        <div>
          <div className="text-2xl font-black text-white italic uppercase tracking-tight">OpenF1 API</div>
          <div className="text-xs text-green-400 flex items-center gap-2 font-bold mt-1 uppercase tracking-wider"><Activity size={12} className="animate-pulse" /> Operational</div>
        </div>
      </div>
      <div className="bg-black/40 backdrop-blur-md rounded-sm p-4 font-mono text-[10px] text-slate-400 space-y-2 border border-white/5">
        <div className="flex justify-between"><span>Total Sessions:</span> <span className="text-white font-bold">{bronze?.n_sessions ?? '--'}</span></div>
        <div className="flex justify-between"><span>Seasons:</span> <span className="text-white font-bold">{bronze?.n_seasons ?? '--'}</span></div>
        <div className="flex justify-between"><span>Latest:</span> <span className="text-cyan-400 font-bold truncate ml-4">{latestSessionLabel}</span></div>
      </div>
    </Card>

    <Card title="Transformation" className="!border-orange-500/20" actionIcon={<Layers size={16} className="text-orange-400" />}>
      <div className="flex items-center gap-6 mb-6">
        <div className="p-4 bg-orange-500/10 rounded-sm border border-orange-500/20 shadow-[0_0_20px_rgba(249,115,22,0.2)]"><Layers className="text-orange-400" size={32} /></div>
        <div>
          <div className="text-2xl font-black text-white italic uppercase tracking-tight">dbt Core</div>
          <div className="text-xs text-orange-400 flex items-center gap-2 font-bold mt-1 uppercase tracking-wider"><PlayCircle size={12} className="animate-spin" /> Batch Running</div>
        </div>
      </div>
      <div className="space-y-2 font-mono text-[10px]">
        <div className="flex justify-between text-slate-400 bg-white/5 p-2 rounded-sm border border-white/5 items-center">
          <span>bronze.sessions</span>
          <Badge color={bronze && bronze.n_sessions > 0 ? 'green' : 'red'}>
            {bronze && bronze.n_sessions > 0 ? 'Ready' : 'Empty'}
          </Badge>
        </div>
        <div className="flex justify-between text-slate-400 bg-white/5 p-2 rounded-sm border border-white/5 items-center">
          <span>bronze.session_result</span>
          <Badge color={bronze && (bronze.n_result_rows || 0) > 0 ? 'green' : 'yellow'}>
            {bronze && (bronze.n_result_rows || 0) > 0 ? 'Ready' : 'No Rows'}
          </Badge>
        </div>
        <div className="flex justify-between text-slate-400 bg-white/5 p-2 rounded-sm border border-white/5 items-center relative overflow-hidden">
          <span>gold.predictions.race_win</span>
          <Badge color={predictionsInfo && predictionsInfo.n_rows > 0 ? 'green' : 'yellow'}>
            {predictionsInfo && predictionsInfo.n_rows > 0 ? 'Ready' : 'Waiting'}
          </Badge>
          <div className="absolute bottom-0 left-0 h-0.5 bg-orange-400 animate-[loading_2s_ease-in-out_infinite]" style={{width: '30%'}}></div>
        </div>
      </div>
    </Card>

    <Card title="Inference" className="!border-purple-500/20" actionIcon={<Cpu size={16} className="text-purple-400" />}>
      <div className="flex items-center gap-6 mb-6">
        <div className="p-4 bg-purple-500/10 rounded-sm border border-purple-500/20 shadow-[0_0_20px_rgba(168,85,247,0.2)]"><Cpu className="text-purple-400" size={32} /></div>
        <div>
          <div className="text-2xl font-black text-white italic uppercase tracking-tight">Race Win Model v2</div>
          <div className="text-xs text-purple-400 flex items-center gap-2 font-bold mt-1 uppercase tracking-wider"><Zap size={12} /> Ready</div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 text-center">
         <div className="bg-white/5 p-3 rounded-sm border border-white/5">
           <div className="text-[9px] text-slate-500 uppercase font-black tracking-widest mb-1">Top-1 Hit Rate</div>
           <div className="text-2xl font-black text-white italic">{hit1Pct}%</div>
         </div>
         <div className="bg-white/5 p-3 rounded-sm border border-white/5">
           <div className="text-[9px] text-slate-500 uppercase font-black tracking-widest mb-1">Top-3 Hit Rate</div>
           <div className="text-2xl font-black text-white italic">{hit3Pct}%</div>
         </div>
      </div>
    </Card>
    
    <Card className="md:col-span-3 bg-[#050505] font-mono text-xs p-0 overflow-hidden border-white/10" title="System Logs" actionIcon={<Code size={16} className="text-slate-500" />}>
      <div className="bg-white/5 px-6 py-2 border-b border-white/10 text-slate-400 flex justify-between items-center text-[10px] uppercase tracking-wider font-bold">
        <span>Live Stream</span>
        <span className="flex gap-2">
          <div className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_5px_rgba(239,68,68,0.8)]"></div>
          <div className="w-2 h-2 rounded-full bg-yellow-500 shadow-[0_0_5px_rgba(234,179,8,0.8)]"></div>
          <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_5px_rgba(34,197,94,0.8)] animate-pulse"></div>
        </span>
      </div>
      <div className="p-4 space-y-2 h-40 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 text-[11px]">
        {(() => {
          const entries: { time: string; level: 'INFO' | 'SUCCESS' | 'WARN' | 'DEBUG'; message: string }[] = [];
          const now = new Date();
          const time = now.toTimeString().slice(0, 8);
          if (bronze) {
            entries.push({
              time,
              level: 'INFO',
              message: `Bronze ingestion healthy – ${bronze.n_sessions ?? 0} sessions across ${bronze.n_seasons ?? 0} seasons.`,
            });
            if (typeof bronze.n_result_rows === 'number') {
              entries.push({
                time,
                level: 'SUCCESS',
                message: `Session results loaded – ${bronze.n_result_rows} classification rows.`,
              });
            }
          }
          if (predictionsInfo) {
            entries.push({
              time,
              level: 'INFO',
              message: `predictions.race_win ready with ${predictionsInfo.n_rows ?? 0} rows for season ${predictionsInfo.season ?? modelSummary?.season ?? ''}.`,
            });
          }
          if (modelSummary) {
            entries.push({
              time,
              level: 'DEBUG',
              message: `Model hit@1=${(modelSummary.hit_at_1 * 100).toFixed(1)}% · hit@3=${(modelSummary.hit_at_3 * 100).toFixed(1)}% over ${modelSummary.n_races} races.`,
            });
          }
          if (!entries.length) {
            entries.push({
              time,
              level: 'INFO',
              message: 'DE monitor online – waiting for metrics.',
            });
          }
          return entries.map((log, idx) => {
            const levelClass =
              log.level === 'SUCCESS'
                ? 'text-green-500'
                : log.level === 'WARN'
                ? 'text-yellow-500'
                : log.level === 'DEBUG'
                ? 'text-cyan-500'
                : 'text-blue-500';
            return (
              <p key={idx} className="text-slate-500">
                <span className="text-slate-700 pr-3">[{log.time}]</span>{' '}
                <span className={`${levelClass} font-bold`}>{log.level}</span>{' '}
                {log.message}
              </p>
            );
          });
        })()}
      </div>
    </Card>
  </div>
  );
};

// --- Main Layouts ---

const LandingPage = ({ onEnter }: { onEnter: () => void }) => (
  <div
    className="min-h-screen text-white font-sans relative overflow-hidden selection:bg-red-500 selection:text-black"
    style={{
      backgroundImage: `linear-gradient(120deg, rgba(15,23,42,0.8) 0%, rgba(30,41,59,0.7) 40%, rgba(15,23,42,0.8) 100%), url(${LandingHeroImage})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      backgroundColor: '#0b0f1a',
    }}
  >
    {/* Animated Background Grid */}
    <div className="absolute inset-0 z-0 opacity-25">
      <div className="absolute inset-0" style={{backgroundImage: 'linear-gradient(rgba(255,255,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px)', backgroundSize: '40px 40px', transform: 'perspective(500px) rotateX(60deg) translateY(-100px) scale(3)'}}></div>
    </div>

    {/* Light Orbs */}
    <div className="absolute top-1/4 left-1/4 w-[520px] h-[520px] bg-gradient-to-br from-[#e50914]/35 via-transparent to-transparent rounded-full blur-[150px] animate-pulse"></div>
    <div className="absolute bottom-1/4 right-1/4 w-[520px] h-[520px] bg-gradient-to-tr from-[#9ca3af]/40 via-[#0b0f1a]/50 to-transparent rounded-full blur-[150px] animate-pulse delay-700"></div>

    {/* Hero Content */}
    <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6">
      <div className="text-center max-w-5xl">
        <div className="flex items-center justify-center gap-4 mb-8 animate-in slide-in-from-bottom-10 duration-700 fade-in">
          <span className="px-4 py-1.5 border border-white/40 text-slate-100 text-[10px] font-black tracking-[0.3em] uppercase rounded-sm bg-white/10 backdrop-blur-md shadow-[0_0_30px_rgba(255,255,255,0.12)]">Data Engineering Portfolio</span>
        </div>
        
        <h1
          className="text-7xl md:text-[10rem] font-black leading-none tracking-tighter mb-3 italic transform -skew-x-6 relative z-10"
          style={{
            backgroundImage:
              'linear-gradient(120deg, #f8f8f8 0%, #cfd3d8 25%, #9ca3af 50%, #e5e7eb 75%, #f8f8f8 100%)',
            WebkitBackgroundClip: 'text',
            color: 'transparent',
            textShadow: '0 0 60px rgba(255,255,255,0.35), 0 0 18px rgba(229,9,20,0.45)',
          }}
        >
          F1 <span className="text-transparent bg-clip-text bg-gradient-to-b from-[#fdfdfd] via-[#d6d9dc] to-[#9ca3af]">LakeHouse</span>
          <span className="absolute -inset-x-6 inset-y-6 pointer-events-none bg-[radial-gradient(circle_at_50%_15%,rgba(255,255,255,0.45),transparent_35%),radial-gradient(circle_at_80%_60%,rgba(229,9,20,0.2),transparent_35%)] blur-3xl opacity-60"></span>
        </h1>
        
        <p className="text-sm md:text-base text-slate-200 max-w-2xl mx-auto mb-10 font-bold tracking-[0.3em] uppercase animate-in slide-in-from-bottom-10 duration-1000 delay-150 fade-in">
          By: <span className="text-white ml-2">Shravan Sulikeri</span>
        </p>

        <p className="text-xl md:text-2xl text-slate-100 max-w-2xl mx-auto mb-16 font-bold tracking-widest uppercase animate-in slide-in-from-bottom-10 duration-1000 delay-250 fade-in">
          The <span className="text-[#e50914]">Lakehouse</span> & <span className="text-slate-50">Analytics</span> Platform
        </p>

        {/* Central "Car" or Abstract Visual */}
        <div className="relative w-full max-w-xl mx-auto h-72 md:h-96 mb-16 animate-in fade-in duration-1000 delay-300 group cursor-pointer perspective-1000" onClick={onEnter}>
           {/* Abstract Wireframe Car shape */}
           <svg viewBox="0 0 400 200" className="w-full h-full stroke-white fill-none stroke-[0.5] drop-shadow-[0_0_20px_rgba(255,255,255,0.3)] group-hover:drop-shadow-[0_0_40px_rgba(255,255,255,0.6)] transition-all duration-500 group-hover:scale-105 group-hover:rotate-x-12 transform-gpu">
             <path d="M50,150 L100,150 M300,150 L350,150" strokeWidth="2" className="animate-pulse" /> {/* Tires Ground */}
             <path d="M40,140 A20,20 0 1,1 80,140" strokeWidth="1" /> {/* Wheel */}
             <path d="M320,140 A20,20 0 1,1 360,140" strokeWidth="1" /> {/* Wheel */}
             <path d="M10,130 L40,130 L50,110 L120,110 L140,80 L220,80 L240,110 L350,110 L380,120" strokeWidth="1" /> {/* Body Line */}
             <line x1="140" y1="80" x2="220" y2="80" strokeWidth="1" />
             <path d="M120,110 L240,110" opacity="0.3" />
             {/* Flow lines */}
             <path d="M-100,100 L500,100" stroke="white" opacity="0.1" strokeWidth="0.5" className="animate-[flow_3s_linear_infinite]" />
             <path d="M-100,120 L500,120" stroke="white" opacity="0.1" strokeWidth="0.5" className="animate-[flow_3s_linear_infinite_0.5s]" />
             <path d="M-100,140 L500,140" stroke="white" opacity="0.1" strokeWidth="0.5" className="animate-[flow_3s_linear_infinite_1s]" />
             <style>{`@keyframes flow { 0% { stroke-dashoffset: 600; } 100% { stroke-dashoffset: 0; } } path.animate-flow { stroke-dasharray: 600; }`}</style>
           </svg>
           
           <div className="absolute inset-0 flex items-center justify-center">
             <button
               onClick={onEnter}
               className="relative inline-flex items-center justify-center px-14 py-4 rounded-full font-black tracking-[0.25em] uppercase text-[#0f172a] bg-gradient-to-r from-[#d9d9d9] via-[#f5f5f5] to-[#d0d0d0] shadow-[0_18px_60px_rgba(0,0,0,0.35)] border border-white/30 backdrop-blur-sm overflow-hidden transition duration-400 group/btn hover:scale-105 hover:shadow-[0_22px_90px_rgba(229,9,20,0.45)]"
             >
               <span className="relative z-20 drop-shadow-[0_2px_4px_rgba(255,255,255,0.6)]">ENTER PITWALL</span>
               <span className="absolute inset-0 bg-gradient-to-r from-[#e50914]/65 via-transparent to-transparent opacity-0 group-hover/btn:opacity-100 transition-opacity duration-400"></span>
               <span className="absolute inset-[1px] rounded-full bg-[linear-gradient(120deg,rgba(255,255,255,0.65),rgba(255,255,255,0.08),rgba(255,255,255,0.6))] opacity-60 mix-blend-soft-light"></span>
               <span className="absolute -inset-x-10 -inset-y-6 bg-[radial-gradient(circle_at_30%_50%,rgba(255,255,255,0.5),transparent_45%)] opacity-70"></span>
               <span className="absolute inset-0 bg-[linear-gradient(115deg,rgba(255,255,255,0) 0%,rgba(255,255,255,0.8) 45%,rgba(255,255,255,0) 60%)] translate-x-[-120%] group-hover/btn:translate-x-[120%] transition-transform duration-700 ease-out"></span>
             </button>
           </div>
        </div>

          {/* Tech Stack Footer */}
          <div className="flex flex-wrap justify-center gap-8 md:gap-16 text-slate-400 font-black uppercase tracking-widest text-xs animate-in slide-in-from-bottom-5 duration-1000 delay-500">
            <div className="flex items-center gap-2 hover:text-white transition-colors"><Database size={14} /> DuckDB</div>
            <div className="flex items-center gap-2 hover:text-white transition-colors"><Layers size={14} /> dbt Core</div>
            <div className="flex items-center gap-2 hover:text-white transition-colors"><Box size={14} /> Docker</div>
            <div className="flex items-center gap-2 hover:text-white transition-colors"><Activity size={14} /> FastAPI</div>
            <div className="flex items-center gap-2 hover:text-white transition-colors"><Code size={14} /> React</div>
          </div>
      </div>
    </div>
  </div>
);

const DashboardLayout = ({ setView }: { setView: (view: string) => void }) => {
  const [activeTab, setActiveTab] = useState('home');
  const [availableSeasons, setAvailableSeasons] = useState<number[]>([]);
  const [availableRaces, setAvailableRaces] = useState<RaceMeta[]>([]);
  const [selectedSeason, setSelectedSeason] = useState<number | null>(null);
  const [selectedRace, setSelectedRace] = useState<RaceMeta | null>(null);
  const [manualRound, setManualRound] = useState<number>(1); // fallback when meta not loaded
  const [summary, setSummary] = useState<PredictionSummary | null>(null);
  const [monitor, setMonitor] = useState<MonitorPayload | null>(null);
  const [raceResults, setRaceResults] = useState<SessionResultRow[]>([]);
  const [sessionResults, setSessionResults] = useState<SessionResultRow[]>([]);
  const [sessions, setSessions] = useState<SessionMeta[]>([]);
  const [selectedSessionType, setSelectedSessionType] = useState<string>('R');
  const [driverStandings, setDriverStandings] = useState<DriverStanding[]>([]);
  const [constructorStandings, setConstructorStandings] = useState<ConstructorStanding[]>([]);
  const [teamStandings, setTeamStandings] = useState<TeamStanding[]>([]);
  const [raceWeather, setRaceWeather] = useState<WeatherSummary>({ rain: null, trackTemp: null, airTemp: null, windSpeed: null, humidity: null });
  const [racePredictions, setRacePredictions] = useState<RacePrediction[]>([]);
  const [driverPace, setDriverPace] = useState<DriverPaceMap>({});
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLoadingMeta, setIsLoadingMeta] = useState(false);
  const [metaError, setMetaError] = useState<string | null>(null);
  const [refreshIndex, setRefreshIndex] = useState(0);

  const handleSeasonChange = (value: number) => {
    setSelectedSeason(value);
    setSelectedRace(null);
  };

  const handleRaceChange = (value: number) => {
    if (availableRaces.length > 0) {
      const match = availableRaces.find((r) => r.round === value);
      if (match) setSelectedRace(match);
    } else {
      setManualRound(value);
    }
  };

  useEffect(() => {
    const loadSeasons = async () => {
      try {
        setIsLoadingMeta(true);
        setMetaError(null);
        const res = await fetch(`${API_BASE_URL}/api/meta/seasons`);
        if (!res.ok) throw new Error('Failed to load seasons');
        const data = await res.json();
        // API returns objects; normalize to season numbers only to avoid rendering objects as children
        const seasonsRaw = data?.seasons || [];
        const seasons: number[] = seasonsRaw
          .map((s: any) => (typeof s === 'number' ? s : s?.season))
          .filter((s: number | undefined | null): s is number => typeof s === 'number');
        setAvailableSeasons(seasons);
        if (!selectedSeason && seasons.length > 0) {
          setSelectedSeason(seasons[seasons.length - 1]);
        }
      } catch (_err: any) {
        setMetaError(_err?.message || 'Failed to load seasons');
        if (!availableSeasons.length) {
          setAvailableSeasons([2023, 2024]);
          if (!selectedSeason) setSelectedSeason(2024);
        }
      } finally {
        setIsLoadingMeta(false);
      }
    };
    loadSeasons();
  }, []);

  useEffect(() => {
    const loadRaces = async () => {
      if (!selectedSeason) return;
      try {
        setIsLoadingMeta(true);
        setMetaError(null);
        const res = await fetch(`${API_BASE_URL}/api/meta/races?season=${selectedSeason}`);
        if (!res.ok) throw new Error('Failed to load races');
        const data = await res.json();
        const races: (RaceMeta & { display_round?: number })[] = data || [];
        setAvailableRaces(races);
        // Default to the first race (round 1) when the page loads.
        if (!selectedRace && races.length > 0) {
          setSelectedRace(races[0]);
          setManualRound(races[0].round);
        }
      } catch (_err: any) {
        setMetaError(_err?.message || 'Failed to load races');
        setAvailableRaces([]);
        if (!selectedRace) setSelectedRace(null);
      } finally {
        setIsLoadingMeta(false);
      }
    };
    loadRaces();
  }, [selectedSeason, refreshIndex]);

  useEffect(() => {
    const loadSummary = async () => {
      if (!selectedSeason) return;
      try {
        const res = await fetch(`${API_BASE_URL}/api/predictions/race_win/summary?season=${selectedSeason}`);
        if (res.ok) {
          const data = await res.json();
          setSummary(data);
        }
      } catch (_err) {
        // ignore summary errors silently to avoid UI changes
      }
    };
    loadSummary();
  }, [selectedSeason, refreshIndex]);

  useEffect(() => {
    const loadMonitor = async () => {
      if (!selectedSeason) return;
      try {
        const res = await fetch(`${API_BASE_URL}/api/monitor?season=${selectedSeason}`);
        if (!res.ok) throw new Error('Failed to load monitor');
        const data: MonitorPayload = await res.json();
        setMonitor(data);
      } catch (_err) {
        setMonitor(null);
      }
    };
    loadMonitor();
  }, [selectedSeason, refreshIndex]);

  useEffect(() => {
    const loadRaceResults = async () => {
      if (!selectedSeason) return;
      if (!selectedRace && !availableRaces.length) return;
      try {
        const round = selectedRace?.round ?? manualRound;
        const res = await fetch(`${API_BASE_URL}/api/races/${selectedSeason}/${round}/results?session_type=R`);
        if (!res.ok) throw new Error('Failed to load results');
        const data: SessionResultRow[] = await res.json();
        setRaceResults(data);
      } catch (_err) {
        setRaceResults([]);
      }
    };
    loadRaceResults();
  }, [selectedSeason, selectedRace, refreshIndex, availableRaces, manualRound]);

  useEffect(() => {
    const loadSessions = async () => {
      if (!selectedSeason || !(selectedRace || manualRound)) return;
      try {
        const round = selectedRace?.round ?? manualRound;
        const res = await fetch(`${API_BASE_URL}/api/races/${selectedSeason}/${round}/sessions`);
        if (!res.ok) throw new Error('Failed to load sessions');
        const data = await res.json();
        const list = data.sessions || [];
        setSessions(list);
        if (list.length) {
          const raceSession = list.find((s: SessionMeta) => s.session_type === 'R') || list[list.length - 1];
          setSelectedSessionType(raceSession.session_type);
        }
      } catch (_err) {
        setSessions([]);
      }
    };
    loadSessions();
  }, [selectedSeason, selectedRace, manualRound, refreshIndex, availableRaces]);

  useEffect(() => {
    const loadWeather = async () => {
      if (!selectedSeason || (!selectedRace && !availableRaces.length)) return;
      try {
        const round = selectedRace?.round ?? manualRound;
        const res = await fetch(`${API_BASE_URL}/api/races/${selectedSeason}/${round}/weather?session_type=R`);
        if (!res.ok) throw new Error('Failed to load weather');
        const data = await res.json();
        const rainVal = data.rain ?? data.rain_probability ?? data.rain_prob ?? null;
        const trackTemp = data.track_temp_c ?? data.track_temp ?? null;
        const airTemp = data.air_temp_c ?? data.air_temp ?? null;
        const windSpeed = data.wind_speed ?? data.wind_speed_kmh ?? null;
        const humidity = data.humidity ?? data.humidity_pct ?? null;
        setRaceWeather({ rain: rainVal, trackTemp, airTemp, windSpeed, humidity });
      } catch (_err) {
        setRaceWeather({ rain: null, trackTemp: null, airTemp: null, windSpeed: null, humidity: null });
      }
    };
    loadWeather();
  }, [selectedSeason, selectedRace, manualRound, refreshIndex, availableRaces]);

  useEffect(() => {
    const loadRacePreds = async () => {
      if (!selectedSeason || (!selectedRace && !availableRaces.length)) return;
      try {
        const round = selectedRace?.round ?? manualRound;
        const res = await fetch(`${API_BASE_URL}/api/races/${selectedSeason}/${round}/predictions`);
        if (!res.ok) throw new Error('Failed to load predictions');
        const data = await res.json();
        const field = data.field || [];
        const mapped: RacePrediction[] = field.map((f: any) => ({
          season: selectedSeason ?? 2024,
          round: round ?? 1,
          driver_code: f.driver_code,
          driver_name: f.driver_name || null,
          team_name: f.team_name || null,
          pred_win_proba: f.p_win ?? 0,
          grid_position: f.grid_position ?? null,
          pred_win_proba_softmax: f.p_top3 ?? undefined,
        }));
        setRacePredictions(mapped);
      } catch (_err) {
        setRacePredictions([]);
      }
    };
    loadRacePreds();
  }, [selectedSeason, selectedRace, manualRound, refreshIndex]);

  useEffect(() => {
    const loadSessionResults = async () => {
      if (!selectedSeason || (!selectedRace && !availableRaces.length) || !selectedSessionType) return;
      try {
        const round = selectedRace?.round ?? manualRound;
        const res = await fetch(`${API_BASE_URL}/api/races/${selectedSeason}/${round}/results?session_type=${selectedSessionType}`);
        if (!res.ok) throw new Error('Failed to load session results');
        const data: SessionResultRow[] = await res.json();
        setSessionResults(data);
      } catch (_err) {
        setSessionResults([]);
      }
    };
    loadSessionResults();
  }, [selectedSeason, selectedRace, manualRound, selectedSessionType, refreshIndex, availableRaces]);

  useEffect(() => {
    const loadStandings = async () => {
      if (!selectedSeason) return;
      try {
        const round = selectedRace?.round ?? manualRound;
        const roundParam = round ? `&round=${round}` : "";
        
        const resDrivers = await fetch(`${API_BASE_URL}/api/standings/drivers?season=${selectedSeason}${roundParam}`);
        if (resDrivers.ok) {
          const data: DriverStanding[] = await resDrivers.json();
          setDriverStandings(data);
        }
        const resTeams = await fetch(`${API_BASE_URL}/api/standings/constructors?season=${selectedSeason}${roundParam}`);
        if (resTeams.ok) {
          const data: ConstructorStanding[] = await resTeams.json();
          setConstructorStandings(data);
        }
        const resTeamsDetail = await fetch(`${API_BASE_URL}/api/standings/teams?season=${selectedSeason}${roundParam}`);
        if (resTeamsDetail.ok) {
          const data: TeamStanding[] = await resTeamsDetail.json();
          setTeamStandings(data);
        }
      } catch (_err) {
        setDriverStandings([]);
        setConstructorStandings([]);
        setTeamStandings([]);
      }
    };
    loadStandings();
  }, [selectedSeason, selectedRace, manualRound, refreshIndex]);

  useEffect(() => {
    const loadPace = async () => {
      if (!selectedSeason) return;
      try {
        const res = await fetch(`${API_BASE_URL}/api/season/${selectedSeason}/driver_pace`);
        if (!res.ok) throw new Error('Failed to load pace');
        const data = await res.json();
        const paceEntries = data?.pace || [];
        const map: DriverPaceMap = {};
        paceEntries.forEach((p: any) => {
          map[p.driver_code] = p.positions || [];
        });
        setDriverPace(map);
      } catch (err) {
        setDriverPace({});
      }
    };
    loadPace();
  }, [selectedSeason, refreshIndex]);

  const activeRace = useMemo(() => {
    if (selectedRace) return raceFromMeta(selectedRace);
    // Get races for current season or fallback to 2025
    const racesByYear: Record<number, Race[]> = {
      2018: RACES_2018,
      2019: RACES_2019,
      2020: RACES_2020,
      2021: RACES_2021,
      2022: RACES_2022,
      2023: RACES_2023,
      2024: RACES_2024,
      2025: RACES_2025,
    };
    const yearRaces = selectedSeason && racesByYear[selectedSeason] ? racesByYear[selectedSeason] : RACES_2025;
    return yearRaces.find(r => r.round === manualRound) || yearRaces[0];
  }, [selectedRace, manualRound, selectedSeason]);

  const topPredictions = useMemo(() => {
    const source: (RacePrediction | SessionResultRow)[] = racePredictions.length ? racePredictions : raceResults;
    return source
      .slice()
      .sort((a, b) => probabilityValue(b) - probabilityValue(a))
      .slice(0, 3);
  }, [racePredictions, raceResults]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setRefreshIndex((i) => i + 1);
    setTimeout(() => setIsRefreshing(false), 2000);
  };

  const handleSessionTypeChange = (code: string) => {
    setSelectedSessionType(code);
  };

  const tabs = [
    { id: 'home', label: 'Home', icon: <Box size={18} /> },
    { id: 'standings', label: 'Standings', icon: <Users size={18} /> },
    { id: 'teams', label: 'Teams', icon: <Trophy size={18} /> },
    { id: 'race', label: 'Race Explorer', icon: <MapIcon size={18} /> },
    { id: 'predictions', label: 'Predictor', icon: <Zap size={18} /> },
    { id: 'history', label: 'History', icon: <History size={18} /> },
    { id: 'pipeline', label: 'DE Monitor', icon: <Server size={18} /> },
    { id: 'strategy', label: 'Data Engineering SkillSet', icon: <TrendingUp size={18} /> },
  ];

  const renderContent = () => {
    switch(activeTab) {
      case 'home': return <HomeView setTab={setActiveTab} activeRace={activeRace} topPredictions={topPredictions} raceResults={raceResults} raceWeather={raceWeather} sessions={sessions} selectedSessionType={selectedSessionType} standingsLeader={driverStandings[0] || null} />;
      case 'standings': return <StandingsView driverStandings={driverStandings} constructorStandings={constructorStandings} driverPace={driverPace} season={selectedSeason} />;
      case 'teams': return <TeamsView teamStandings={teamStandings} />;
      case 'race': return <RaceExplorerView activeRace={activeRace} raceWeather={raceWeather} raceResults={raceResults} sessionResults={sessionResults} sessions={sessions} onSessionChange={handleSessionTypeChange} selectedSessionType={selectedSessionType} />;
      case 'strategy': return <StrategyView />;
      case 'predictions': {
        return <PredictionsLab season={selectedSeason} round={selectedRace?.round ?? manualRound} />;
      }
      case 'history': return <HistoryView driverStandings={driverStandings} constructorStandings={constructorStandings} />;
      case 'pipeline': return <PipelineView summary={summary} monitor={monitor} />;
      default: return <HomeView setTab={setActiveTab} activeRace={activeRace} topPredictions={topPredictions} raceResults={raceResults} raceWeather={raceWeather} sessions={sessions} selectedSessionType={selectedSessionType} standingsLeader={driverStandings[0] || null} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-white font-sans flex overflow-hidden relative selection:bg-red-500 selection:text-white">
      {/* Subtle animated background mesh */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-10">
         <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="white" strokeWidth="0.5"/>
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
         </svg>
      </div>

      {/* Sidebar */}
      <aside className="w-20 lg:w-64 bg-black/80 backdrop-blur-xl border-r border-white/5 flex flex-col shrink-0 relative z-20">
        <div className="h-20 flex items-center justify-center lg:justify-start lg:px-6 border-b border-white/5 relative group cursor-pointer" onClick={() => setView('landing')}>
          <img
            src={F1LakehouseLogo}
            alt="F1 Lakehouse"
            className="h-16 lg:h-20 w-auto relative z-10 skew-x-[-10deg] object-contain brightness-110 drop-shadow-[0_0_12px_rgba(255,255,255,0.18)]"
          />
        </div>
        
        <nav className="flex-1 py-8 space-y-2 px-3">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-4 px-4 py-3 rounded-sm transition-all duration-200 group relative overflow-hidden ${activeTab === tab.id ? 'bg-red-600 text-white shadow-[0_0_20px_rgba(220,38,38,0.4)] skew-x-[-10deg]' : 'text-slate-500 hover:text-white hover:bg-white/5 skew-x-[-10deg]'}`}
            >
              <span className={`relative z-10 transition-colors skew-x-[10deg] ${activeTab === tab.id ? 'text-white' : 'text-slate-500 group-hover:text-white'}`}>{tab.icon}</span>
              <span className="hidden lg:block font-black text-xs uppercase tracking-widest relative z-10 skew-x-[10deg]">{tab.label}</span>
            </button>
          ))}
        </nav>

        <div className="p-6 border-t border-white/5">
          <div className="bg-white/5 rounded-sm p-3 flex items-center gap-4 cursor-pointer hover:bg-white/10 transition-all duration-300 border border-white/5 group relative overflow-hidden">
             <div className="w-8 h-8 rounded-sm bg-gradient-to-tr from-red-600 to-orange-600 flex items-center justify-center text-[10px] font-black shadow-lg relative z-10">DE</div>
             <div className="hidden lg:block overflow-hidden relative z-10">
               <div className="text-xs font-bold text-white uppercase tracking-wider">Admin</div>
               <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Engineer</div>
             </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative z-10">
        {/* Header / Global Filters */}
        <header className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-black/60 backdrop-blur-md z-20">
          <div className="flex items-center gap-6">
        <div className="relative group" title={metaError || ''}>
           <div className="flex items-center gap-3 text-sm font-bold text-slate-300 hover:text-white transition-colors uppercase tracking-wider pointer-events-none">
             <span className="text-red-500 font-black">{selectedSeason ?? '----'}</span> Season <ChevronDown size={14} className="text-slate-500" />
           </div>
           <select 
             value={selectedSeason ?? (availableSeasons[availableSeasons.length - 1] ?? 2025)}
             onChange={(e) => handleSeasonChange(Number(e.target.value))}
             disabled={isLoadingMeta}
             className="absolute inset-0 opacity-0 cursor-pointer"
           >
             {(availableSeasons.length ? availableSeasons : [selectedSeason || 2025]).map((s) => (
               <option key={s} value={s}>{s}</option>
             ))}
           </select>
         </div>
             <div className="h-4 w-px bg-white/10 skew-x-[-20deg]"></div>
             <div className="relative group">
               <select 
                  value={selectedRace?.round ?? manualRound}
                  onChange={(e) => handleRaceChange(Number(e.target.value))}
                  disabled={isLoadingMeta}
                  className="bg-transparent text-sm font-bold text-white uppercase tracking-wider outline-none cursor-pointer appearance-none flex items-center gap-3"
                  style={{backgroundImage: 'none'}}
               >
                 {(() => {
                   const racesByYear: Record<number, Race[]> = {
                     2018: RACES_2018,
                     2019: RACES_2019,
                     2020: RACES_2020,
                     2021: RACES_2021,
                     2022: RACES_2022,
                     2023: RACES_2023,
                     2024: RACES_2024,
                     2025: RACES_2025,
                   };
                   const fallbackRaces = selectedSeason && racesByYear[selectedSeason] ? racesByYear[selectedSeason] : RACES_2025;
                   return (availableRaces.length ? availableRaces : fallbackRaces).map((r, idx) => {
                     const anyRace = r as any;
                     const labelRound = typeof anyRace.display_round === 'number' ? anyRace.display_round : (r as Race).round ?? (idx + 1);
                     const labelName = 'display_name' in anyRace ? anyRace.display_name : (r as Race).name;
                     return (
                       <option key={r.round} value={r.round} className="bg-slate-900 text-slate-300">
                         {labelRound}. {labelName}
                       </option>
                     );
                   });
                 })()}
               </select>
               <ChevronDown size={14} className="text-slate-500 absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none" />
             </div>
          </div>
          
          <div className="flex items-center gap-4">
            <button 
              onClick={handleRefresh}
              className={`bg-white text-black px-6 py-2 rounded-sm text-[10px] font-black tracking-[0.15em] uppercase hover:bg-red-500 hover:text-white transition-all flex items-center gap-3 skew-x-[-10deg] ${isRefreshing ? 'opacity-80 cursor-wait' : ''}`}
            >
              <span className="skew-x-[10deg] flex items-center gap-2">
                {isRefreshing ? <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"></div> : <Database size={14} />}
                {isRefreshing ? 'SYNCING...' : 'REFRESH'}
              </span>
            </button>
          </div>
        </header>

        {/* Scrollable View Area */}
        <div className="flex-1 overflow-y-auto p-8 lg:p-12 scrollbar-thin scrollbar-thumb-red-600 scrollbar-track-transparent">
          <div className="max-w-[1600px] mx-auto">
             <div className="flex justify-between items-end mb-12 animate-in slide-in-from-top-4 duration-500">
               <div>
                 <h1 className="text-6xl font-black text-white uppercase tracking-tighter italic mb-2 transform -skew-x-6">
                   {activeTab === 'strategy' ? 'Data Engineering SkillSet' : activeTab.replace('-', ' ')}
                 </h1>
                 <p className="text-slate-500 text-xs font-bold uppercase tracking-[0.2em] flex items-center gap-2">
                   <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.8)]"></span>
                   Live Telemetry Feed // Lakehouse Connection Active
                 </p>
               </div>
               {activeTab === 'home' && <Badge color="red">LIVE SESSION</Badge>}
               {activeTab === 'race' && <Badge color="cyan">DATA STREAMING</Badge>}
               {activeTab === 'pipeline' && <Badge color="green">SYSTEM OPTIMAL</Badge>}
             </div>
             
             {renderContent()}
          </div>
        </div>
      </main>
    </div>
  );
};

// --- App Entry ---

export default function App() {
  const [view, setView] = useState('landing'); // 'landing' | 'app'

  return (
    <>
      {view === 'landing' ? (
        <LandingPage onEnter={() => setView('app')} />
      ) : (
        <DashboardLayout setView={setView} />
      )}
    </>
  );
}
