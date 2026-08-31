import { NavLink } from 'react-router-dom';
import { Home, LayoutDashboard, MessageSquareText, UserPlus } from 'lucide-react';

const routes = [
  { to: '/', label: 'Home', icon: Home, protected: false },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, protected: true },
  { to: '/profiler', label: 'Profiler', icon: MessageSquareText, protected: true },
  { to: '/register', label: 'Register', icon: UserPlus, protected: false },
];

export default function RouteNav({ compact = false }: { compact?: boolean }) {
  const hasAccess = localStorage.getItem('skillroute_access_granted') === 'true';
  const baseClass = `${compact ? 'w-full justify-start px-3 py-2 text-sm' : 'px-3 py-2 text-sm'} flex items-center gap-2 rounded-lg font-bold transition-colors`;

  return (
    <div className={`flex ${compact ? 'flex-col gap-1' : 'flex-wrap items-center gap-2'}`}>
      {routes.map(({ to, label, icon: Icon, protected: needsAccess }) => {
        if (needsAccess && !hasAccess) {
          return (
            <button
              key={to}
              type="button"
              disabled
              title="Login or use the bypass button first"
              className={`${baseClass} cursor-not-allowed text-slate-300`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          );
        }

        return (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `${baseClass} ${
                isActive
                  ? 'bg-teal-100 text-teal-800'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-teal-700'
              }`
            }
          >
            <Icon className="w-4 h-4" />
            <span>{label}</span>
          </NavLink>
        );
      })}
    </div>
  );
}
