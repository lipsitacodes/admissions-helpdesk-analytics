import React from "react";
import { MapPin, Check } from "lucide-react";

export const CAMPUS_CHOICES = [
  {
    id: "bhubaneswar",
    name: "Bhubaneswar Campus",
    city: "Bhubaneswar",
    badge: "BBSR",
  },
  {
    id: "paralakhemundi",
    name: "Paralakhemundi Campus",
    city: "Paralakhemundi",
    badge: "PKD",
  },
  {
    id: "all",
    name: "All Campuses (General)",
    city: "All Campuses",
    badge: "CUTM",
  },
];

export function CampusSelector({ selectedCampus, onSelectCampus }) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-light-muted dark:text-dark-muted uppercase px-1">
        <span className="flex items-center gap-1.5">
          <MapPin className="w-3 h-3 text-light-text dark:text-dark-text" />
          <span>Active Campus</span>
        </span>
      </div>

      <div className="grid grid-cols-1 gap-1">
        {CAMPUS_CHOICES.map((campus) => {
          const isSelected = selectedCampus === campus.id;
          return (
            <button
              key={campus.id}
              type="button"
              onClick={() => onSelectCampus(campus.id)}
              className={`w-full flex items-center justify-between px-3 py-2 text-xs rounded-xl font-medium text-left transition-all ${
                isSelected
                  ? "bg-light-surface2 dark:bg-dark-surface2 text-light-text dark:text-dark-text border border-light-borderLight dark:border-dark-borderLight font-semibold shadow-sm"
                  : "text-light-muted dark:text-dark-muted hover:text-light-text dark:hover:text-dark-text hover:bg-light-surface2 dark:hover:bg-dark-surface2 border border-transparent"
              }`}
            >
              <div className="flex items-center gap-2 truncate">
                <span
                  className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                    isSelected ? "bg-purple-600 dark:bg-purple-400" : "bg-light-muted dark:bg-dark-muted opacity-40"
                  }`}
                />
                <span className="truncate">{campus.name}</span>
              </div>

              {isSelected && (
                <Check className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400 shrink-0 ml-1" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default CampusSelector;
