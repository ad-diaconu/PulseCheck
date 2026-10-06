import { useRef, useState, useEffect } from "react";
import { ChevronsUpDown, LogOut } from "lucide-react";

type UserMenuProps = {
  name: string | null;
  email: string;
  isCollapsed: boolean;
  onLogout: () => void;
};

function getInitials(name: string | null, email: string) {
  if (name) {
    return name
      .split(" ")
      .map((word) => word[0])
      .join("")
      .slice(0, 2)
      .toUpperCase();
  }
  return email.slice(0, 2).toUpperCase();
}

const UserMenu = ({ name, email, isCollapsed, onLogout }: UserMenuProps) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={menuRef} className="relative">
      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 w-full min-w-[200px] bg-white border border-slate-200 rounded-lg shadow-lg py-1 z-10">
          <div className="px-3 py-2 text-sm text-slate-500 truncate border-b border-slate-100">
            {email}
          </div>
          <button
            type="button"
            onClick={onLogout}
            className="cursor-pointer flex items-center gap-2 w-full px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      )}

      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="cursor-pointer flex items-center gap-2 w-full px-2 py-2 rounded-lg hover:bg-slate-50 transition-colors"
      >
        <div className="w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center shrink-0 text-xs font-medium text-slate-700">
          {getInitials(name, email)}
        </div>
        {!isCollapsed && (
          <>
            <span className="text-sm font-medium text-slate-900 truncate flex-1 text-left">
              {name ?? email}
            </span>
            <ChevronsUpDown className="w-4 h-4 text-slate-400 shrink-0" />
          </>
        )}
      </button>
    </div>
  );
};

export default UserMenu;
