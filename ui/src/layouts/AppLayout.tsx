import { NavLink, Outlet, useLocation } from "react-router-dom";
import TopBar from "../components/TopBar";
import { useEffect, useState } from "react";
import UserMenu from "../components/UserMenu";
import { useAuth } from "../context/useAuth";
import { WorkspaceProvider } from "../context/WorkspaceContext";
import { api } from "../services/api";
import type { Invitation } from "../types/invitation";
import { Inbox, Activity, ChevronDown, Layers } from "lucide-react";

type FlatNavItem = {
  label: string;
  to: string;
};

type NavGroup = {
  label: string;
  children: FlatNavItem[];
};

const TOP_NAV: FlatNavItem[] = [
  { label: "Monitors", to: "/dashboard" },
  { label: "Inbox", to: "/dashboard/inbox" },
];

const NAV_GROUP: NavGroup = {
  label: "Workspace",
  children: [
    { label: "Statistics", to: "/dashboard/statistics" },
    { label: "Workspaces", to: "/dashboard/workspaces" },
    { label: "Settings", to: "/dashboard/settings" },
  ],
};

const ALL_NAV_ITEMS = [...TOP_NAV, ...NAV_GROUP.children];

const AppLayout = () => {
  const location = useLocation();
  const [isSideBarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [isGroupOpen, setIsGroupOpen] = useState<boolean>(true);
  const [pendingCount, setPendingCount] = useState<number>(0);
  const { logout, user } = useAuth();
  const toggleSidebbar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  useEffect(() => {
    const fetchPendingCount = async () => {
      try {
        const response = await api.get<Invitation[]>("/invitations");
        setPendingCount(response.data.length);
      } catch {
        setPendingCount(0);
      }
    };

    fetchPendingCount();
  }, [location.pathname]);

  const currentLabel =
    ALL_NAV_ITEMS.find((item) => location.pathname === item.to)?.label ??
    "Monitors";

  return (
    <WorkspaceProvider>
      <div className="flex min-h-screen bg-slate-50">
        <aside
          className={`shrink-0 border-r border-slate-200 bg-white flex flex-col overflow-hidden transition-all duration-200 ${
            isSideBarOpen ? "w-64" : "w-0 border-r-0"
          }`}
        >
          <div className="flex items-center gap-3 px-3 py-4">
            <span className="flex size-9 items-center justify-center rounded-md bg-slate-900 shrink-0">
              <span className="text-white font-bold text-sm">P</span>
            </span>
            {isSideBarOpen && (
              <div className="min-w-0">
                <span className="block text-sm font-semibold text-slate-900 truncate">
                  PulseCheck
                </span>
                <span className="block text-xs text-slate-500 truncate">
                  Uptime monitoring
                </span>
              </div>
            )}
          </div>

          <nav className="flex-1 flex flex-col gap-4 p-3">
            <div className="flex flex-col gap-1">
              {TOP_NAV.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/dashboard"}
                  className={({ isActive }) =>
                    `flex items-center justify-between rounded-md p-2 text-sm transition hover:bg-slate-100 ${
                      isActive
                        ? "text-slate-900 font-semibold"
                        : "text-slate-600 hover:text-slate-900"
                    }`
                  }
                >
                  <span className="flex items-center gap-2.5">
                    {item.label === "Monitors" && (
                      <Activity className="size-[18px] shrink-0" />
                    )}
                    {item.label === "Inbox" && (
                      <Inbox className="size-[18px] shrink-0" />
                    )}
                    {isSideBarOpen && item.label}
                  </span>
                  {item.label === "Inbox" &&
                    pendingCount > 0 &&
                    isSideBarOpen && (
                      <span className="inline-flex size-5 items-center justify-center rounded bg-slate-100 text-xs font-medium text-slate-600">
                        {pendingCount}
                      </span>
                    )}
                </NavLink>
              ))}
            </div>

            <div className="border-t border-slate-200" />

            <div className="flex flex-col gap-1">
              <button
                type="button"
                onClick={() => setIsGroupOpen((prev) => !prev)}
                className="flex w-full items-center justify-between gap-2.5 rounded-md p-2 text-sm text-slate-900 transition hover:bg-slate-100"
              >
                <span className="flex items-center gap-2.5">
                  <Layers className="size-[18px] shrink-0" />
                  {isSideBarOpen && NAV_GROUP.label}
                </span>
                {isSideBarOpen && (
                  <ChevronDown
                    className={`size-4 shrink-0 text-slate-400 transition-transform duration-150 ${
                      isGroupOpen ? "rotate-0" : "-rotate-90"
                    }`}
                  />
                )}
              </button>

              {isGroupOpen && isSideBarOpen && (
                <div className="relative flex flex-col gap-1 pl-4">
                  <div className="absolute inset-y-0 left-[18px] w-px bg-slate-200" />
                  {NAV_GROUP.children.map((item) => (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      className={({ isActive }) =>
                        `relative rounded-md py-1.5 pl-5 pr-3 text-sm transition ${
                          isActive
                            ? "text-slate-900 font-semibold bg-white shadow-sm ring-1 ring-slate-200"
                            : "text-slate-600 hover:text-slate-900"
                        }`
                      }
                    >
                      {item.label}
                    </NavLink>
                  ))}
                </div>
              )}
            </div>
          </nav>

          <UserMenu
            name={user?.name ?? null}
            email={user?.email ?? ""}
            isCollapsed={!isSideBarOpen}
            onLogout={logout}
          />
        </aside>

        <div className="flex-1 min-w-0 flex flex-col">
          <TopBar
            onToggleSidebar={toggleSidebbar}
            breadcrumbs={["Home", currentLabel]}
          />
          <main className="flex-1 min-w-0">
            <Outlet />
          </main>
        </div>
      </div>
    </WorkspaceProvider>
  );
};

export default AppLayout;
