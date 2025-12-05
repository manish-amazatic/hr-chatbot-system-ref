export const getAgentDisplayName = (agentUsed?: string): string => {
  if (!agentUsed) return 'HR Assistant';
  
  const agentMap: Record<string, string> = {
    'handle_leave_query': 'Leave Agent',
    'handle_attendance_query': 'Attendance Agent',
    'handle_payroll_query': 'Payroll Agent',
    'search_hr_policy': 'HR Policy',
  };
  
  return agentMap[agentUsed] || 'HR Assistant';
};

export const getAgentColor = (agentUsed?: string): string => {
  if (!agentUsed) return 'blue';
  
  const colorMap: Record<string, string> = {
    'handle_leave_query': 'green',
    'handle_attendance_query': 'blue',
    'handle_payroll_query': 'orange',
    'search_hr_policy': 'purple',
  };
  
  return colorMap[agentUsed] || 'blue';
};
