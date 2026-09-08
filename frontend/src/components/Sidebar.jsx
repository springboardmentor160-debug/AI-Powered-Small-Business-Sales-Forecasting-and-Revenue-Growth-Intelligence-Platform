import React from "react";
import { UtensilsCrossed, LayoutGrid, Soup, Receipt, Users } from "lucide-react";

const ROLE_LABELS = {
  franchise_owner: "Franchise Owner",
  outlet_manager: "Outlet Manager",
  waiter: "Waiter",
  admin: "Admin",
};

const NAV_BY_ROLE = {
  franchise_owner: ["overview", "menu", "orders"],
  outlet_manager: ["overview", "menu", "orders"],
  waiter: ["overview", "orders"],
  admin: ["overview", "staff"],
};

const NAV_META = {
  overview: { label: "Overview", icon: LayoutGrid },
  menu: { label: "Menu & Stock", icon: Soup },
  orders: { label: "Orders", icon: Receipt },
  staff: { label: "Staff", icon: Users },
};

export default function Sidebar({ role, username, activeTab, setActiveTab }) {
  const tabs = NAV_BY_ROLE[role] || ["overview"];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <UtensilsCrossed color="#fff" size={18} />
        </div>
        MarketMind
      </div>

      {tabs.map((tab) => {
        const Meta = NAV_META[tab];
        const Icon = Meta.icon;
        return (
          <div
            key={tab}
            className={`nav-item ${activeTab === tab ? "active" : ""}`}
            onClick={() => setActiveTab(tab)}
          >
            <Icon size={17} />
            {Meta.label}
          </div>
        );
      })}

      <div className="sidebar-footer">
        Signed in as <strong style={{ color: "#fff" }}>{username}</strong>
        <div>
          <span className="role-pill">{ROLE_LABELS[role] || role}</span>
        </div>
      </div>
    </aside>
  );
}
