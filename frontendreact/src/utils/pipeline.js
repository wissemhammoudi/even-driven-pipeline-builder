export const stepHasType = (step, allowedTypes) => {
  const configType = step.step_config?.config_type
  const stepType = step.type
  const stepTypeEnum = step.step_type
  const allStepTypes = [configType, stepType, stepTypeEnum].filter(Boolean)
  return allStepTypes.some(type => allowedTypes.includes(type))
} 