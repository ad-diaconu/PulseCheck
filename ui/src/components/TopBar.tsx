import { PanelLeft, ChevronRight } from "lucide-react";

type TopBarProps = {
  onToggleSidebar: () => void;
  breadcrumbs: string[];
};

const TopBar = ({ onToggleSidebar, breadcrumbs }: TopBarProps) => {
  return (
    <div className="flex items-center gap-3 h-12 px-4 border-b border-slate-200 bg-white">
      <button
        onClick={onToggleSidebar}
        className="p-1.5 rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-900 transition-colors"
        aria-label="Toggle sidebar"
      >
        <PanelLeft className="w-4 h-4" />
      </button>

      <div className="w-px h-4 bg-slate-200" />

      <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm">
        {breadcrumbs.map((crumb, index) => {
          const isLast = index === breadcrumbs.length - 1;

          return (
            <span key={crumb} className="flex items-center gap-1.5">
              <span className={isLast ? "text-slate-900 font-medium" : "text-slate-500"}>
                {crumb}
              </span>
              {!isLast && <ChevronRight className="w-3.5 h-3.5 text-slate-300" />}
            </span>
          );
        })}
      </nav>
    </div>
  );
};

export default TopBar;
