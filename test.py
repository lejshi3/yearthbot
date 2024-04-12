import re

def extract_resources(input_text):
  resources = {}
  production = {}
  lines = input_text.split('\n')
  for line in lines:
      line = line.strip()
      if not line:
          continue
      if ' - ' in line:
          parts = line.split(' - ')
          resource = parts[0].lower().strip()
          if resource == 'population':
              if '(' in line and ')' in line:
                  # Extract city population data
                  city_data = re.findall(r'\(.*?\)', line)[0]
                  cities = re.findall(r'(\w+\s*\w*)\s+(\d+(?:,\d+)?)', city_data)
                  resources['cities'] = {city.strip(): int(pop.replace(',', '')) for city, pop in cities}
              else:
                  quantity = int(parts[1].replace(',', ''))
                  resources[resource] = quantity
          else:
              quantity = int(parts[1].replace(',', ''))
              if len(parts) > 2:
                  prod_parts = parts[2].split()
                  if prod_parts[0] != 'N/A':
                      production[resource] = int(prod_parts[0])
              resources[resource] = quantity
  resources['other'] = []
  return resources, production

input_text = '''
**Del Sol**
Population - 243,174 - N/A
Lumber - 3776 - 513
(-60 to Texas)
Oil - 430 - 45
(+30 from Texas)
Iron - 115 - 20
Precious Metals - 550 - 30
Crops - 3246 - 319
Livestock - 512 - 38
Fish - 2936 - 348
Gold - 1,749 - 199
(-35 TO MORMON)
    (8 Active SEDC, 12 Active SDC)
Sulfur - 510 - 10
Coal - 50 - 0
Ammunition (Sulfur/2 Crops + Precious Metals) - 0
Fuel (Oil/2 Coal) - 0
'''

resources, production = extract_resources(input_text)

print("## Current Resources")
print(resources)
print("## Base Production")
print(production)