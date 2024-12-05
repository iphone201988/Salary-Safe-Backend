import logging

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s'
)

def calculate_internal_component(I, Wi):
  '''Calculates the internal salary component.'''
  return I * Wi

def calculate_external_component(E, We):
  '''Calculates the external salary component.'''
  return E * We

def calculate_skill_premium(skills, skill_weights, market_premiums):
  '''Calculates the skill premium.'''
  return sum(
    proficiency * weight * premium
    for proficiency, weight, premium in zip(
      skills, skill_weights,
      market_premiums
    )
  )

def calculate_location_adjustment(I, location_multiplier):
  '''Calculates the location adjustment.'''
  return I * (location_multiplier - 1)

def calculate_trend_adjustment(I, trend_percentage):
  '''Calculates the trend adjustment.'''
  return (trend_percentage / 100) * I

def calculate_customization_adjustment(C, Wc):
  '''Calculates the customization adjustment.'''
  return C * Wc

def calculate_risk_premium(I, risk_percentage):
  '''Calculates the risk premium.'''
  return (risk_percentage / 100) * I

def calculate_transparency_adjustment(I, transparency_score, transparency_weight):
  '''Calculates the transparency adjustment.'''
  return transparency_score * transparency_weight * I

def calculate_equity_adjustment(equity_score, diversity_premium):
  '''Calculates the diversity and equity adjustment.'''
  return equity_score * diversity_premium

def calculate_flexibility_premium(flexibility_score, flexibility_multiplier):
  '''Calculates the flexibility premium.'''
  return flexibility_score * flexibility_multiplier

def calculate_final_salary(
  I, Wi, E, We, skills, skill_weights, market_premiums,
  location_multiplier, trend_percentage, C, Wc, risk_percentage,
  benefits, transparency_score, transparency_weight,
  equity_score, diversity_premium, flexibility_score,
  flexibility_multiplier, well_being_value, functional_multiplier,
  market_demand_multiplier
):
  '''Main function to calculate the recommended salary.'''
  # Validate inputs
  if not skills or len(skills) != len(skill_weights) or len(skills) != \
  len(market_premiums):
    logging.error('Invalid input: skills, skill_weights, and market_premiums must have the same length.')
    return None

  try:
    internal_component = calculate_internal_component(I, Wi)
    external_component = calculate_external_component(E, We)
    skill_premium = calculate_skill_premium(skills, skill_weights,
    market_premiums)
    location_adjustment = calculate_location_adjustment(I, location_multiplier)
    trend_adjustment = calculate_trend_adjustment(I, trend_percentage)
    customization_adjustment = calculate_customization_adjustment(C, Wc)
    risk_premium = calculate_risk_premium(I, risk_percentage)
    transparency_adjustment = calculate_transparency_adjustment(I,
    transparency_score, transparency_weight)
    equity_adjustment = calculate_equity_adjustment(equity_score,
    diversity_premium)
    flexibility_premium = calculate_flexibility_premium(flexibility_score,
    flexibility_multiplier)

    # Calculate subtotal
    subtotal = (
      internal_component +
      external_component +
      skill_premium +
      location_adjustment +
      trend_adjustment +
      customization_adjustment +
      risk_premium +
      benefits +
      transparency_adjustment +
      equity_adjustment +
      flexibility_premium +
      well_being_value
    )

    # Apply functional and market demand multipliers
    final_salary = subtotal * functional_multiplier * market_demand_multiplier
    return final_salary
  except Exception as e:
    logging.error(f'Error in salary calculation: {e}')
    return None

if __name__ == '__main__':
  # Example Inputs
  I = 85000 # Internal median salary
  Wi = 0.4 # Internal weight
  E = 92000 # External market salary
  We = 0.5 # External weight

  skills = [4, 3, 5] # Proficiency for each skill (scale: 1–5)
  skill_weights = [1.3, 1.1, 1.5] # Weight for each skill
  market_premiums = [3000, 2500, 4000] # Market premium for each skill

  location_multiplier = 1.1 # High-cost region
  trend_percentage = 3 # Forecasted salary trend (3%)

  C = 5000 # Customization factor
  Wc = 0.1 # Customization weight

  risk_percentage = 5 # Risk premium percentage
  benefits = 10000 # Value of benefits/equity

  transparency_score = 4 # Transparency score (1–5)
  transparency_weight = 0.02 # Weight for transparency

  equity_score = 4 # Diversity and equity score (1–5)
  diversity_premium = 2000 # Premium for diversity

  flexibility_score = 3 # Flexibility score (1–5)
  flexibility_multiplier = 1500 # Flexibility multiplier

  well_being_value = 3000 # Well-being benefits value

  functional_multiplier = 1.05 # Industry adjustment (e.g., 5% increase)
  market_demand_multiplier = 1.03 # Market demand adjustment (e.g., 3% increase)

  # Calculate salary
  recommended_salary = calculate_final_salary(
    I, Wi, E, We, skills, skill_weights, market_premiums,
    location_multiplier, trend_percentage, C, Wc, risk_percentage,
    benefits, transparency_score, transparency_weight,
    equity_score, diversity_premium, flexibility_score,
    flexibility_multiplier, well_being_value, functional_multiplier,
    market_demand_multiplier
  )

  if recommended_salary is not None:
    print(f'Recommended Salary: ${recommended_salary:,.2f}')
