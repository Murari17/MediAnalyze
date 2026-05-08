import React from "react";
import Card from "../components/Card";
import { Settings } from "lucide-react";

const SettingsPage = () => {
  return (
    <div className="space-y-6">
      <Card title="Settings" icon={<Settings className="h-4 w-4" />}>
        <p className="text-sm text-[#52525b] dark:text-slate-400">
          Workspace settings and integrations will be available in a future release.
        </p>
      </Card>
    </div>
  );
};

export default SettingsPage;
