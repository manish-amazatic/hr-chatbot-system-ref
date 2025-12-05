export const getAgentDisplayName = (agentUsed?: string): string => {
  if (!agentUsed) return 'HR Assistant';
  
  const agentMap: Record<string, string> = {
    'leave_agent': 'Leave Agent',
    'attendance_agent': 'Attendance Agent',
    'payroll_agent': 'Payroll Agent',
    'hr_policy_search': 'HR Policy RAG',
  };
  
  return agentMap[agentUsed] || 'HR Assistant';
};

export const getAgentColor = (agentUsed?: string): string => {
  if (!agentUsed) return 'blue';
  
  const colorMap: Record<string, string> = {
    'leave_agent': 'green',
    'attendance_agent': 'blue',
    'payroll_agent': 'orange',
    'hr_policy_search': 'purple',
  };
  
  return colorMap[agentUsed] || 'blue';
};
