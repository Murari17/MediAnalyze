import React from "react";
import Card from "../components/Card";
import { Clock } from "lucide-react";

const History = () => {
  return (
    <div className="space-y-6">
      <Card title="History" icon={<Clock className="h-4 w-4" />}>
        <p className="text-sm text-[#52525b] dark:text-slate-400">
          Analysis history will appear here once documents are processed.
        </p>
      </Card>
    </div>
  );
};

export default History;
