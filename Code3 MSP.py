def calculate_msp(  
    material_costs,          # Dict: Material costs (¥/m²) 
    pce=0.10,                # Power conversion efficiency (default 10%)  
    module_area=0.72,         # Module area (m², default 0.72m²)  
    throughput=3.0,           # Production throughput (m²/min, default 3 m²/min, literature baseline)  
    # Baseline operational costs (for 3 m²/min throughput)  
    base_maintenance=2.77,    # Maintenance cost (¥/m²)  
    base_utilities=22.67,     # Utilities cost (¥/m²)  
    base_labor=15.36,         # Labor cost (¥/m²)  
    base_depreciation=13.85,  # Depreciation cost (¥/m²)  
    sga_percent=0.15,         # SG&A percentage (default 15%)  
    tax_rate=0.27,            # Tax rate (default 27%)  
    wacc_percent=0.144,       # WACC (default 14.4%)  
    cost_type={     # 'fixed' (throughput-independent) or 'variable' (throughput-dependent)  
        'maintenance': 'fixed',     
        'utilities': 'variable',    
        'labor': 'variable',        
        'depreciation': 'variable'   
    }  
):  
    # Calculate throughput adjustment factor (baseline: 3 m²/min)  
    # Higher throughput reduces variable costs proportionally  
    throughput_factor = 3.0 / throughput  
      
    # Adjust operational costs based on cost type  
    adjusted_maintenance = base_maintenance if cost_type['maintenance'] == 'fixed' else base_maintenance * throughput_factor  
    adjusted_utilities = base_utilities if cost_type['utilities'] == 'fixed' else base_utilities * throughput_factor  
    adjusted_labor = base_labor if cost_type['labor'] == 'fixed' else base_labor * throughput_factor  
    adjusted_depreciation = base_depreciation if cost_type['depreciation'] == 'fixed' else base_depreciation * throughput_factor  
      
    # Calculate total material cost (direct sum)  
    total_material_cost = sum(material_costs.values())  
      
    # Calculate direct manufacturing cost (materials + adjusted operational costs)  
    direct_manufacturing_cost = (  
        total_material_cost +  
        adjusted_maintenance +  
        adjusted_utilities +  
        adjusted_labor +  
        adjusted_depreciation  
    )  
    # Calculate MSP (per m²)  
    total_cost = direct_manufacturing_cost  
    denominator = 1 - sga_percent - tax_rate - wacc_percent  
    msp_per_m2 = total_cost / denominator if denominator > 0 else float('inf')  
    power_output = module_area * 1000 * pce  # Unit: W 
    msp_per_watt = msp_per_m2 / (1000 * pce)  # Equivalent to msp_per_m2 / (power_output/module_area)  
    return {  
        "MSP (¥/m²)": round(msp_per_m2, 2),  
        "MSP (¥/Wp)": round(msp_per_watt, 2),  
        "Total Material Cost (¥/m²)": round(total_material_cost, 2),  
        "Direct Manufacturing Cost (¥/m²)": round(direct_manufacturing_cost, 2),  
        "Throughput Factor": round(throughput_factor, 2),  
        "Adjusted Maintenance (¥/m²)": round(adjusted_maintenance, 2),  
        "Adjusted Utilities (¥/m²)": round(adjusted_utilities, 2),  
        "Adjusted Labor (¥/m²)": round(adjusted_labor, 2),  
        "Adjusted Depreciation (¥/m²)": round(adjusted_depreciation, 2)  
    }  

material_costs_example = {  
    "Barrier foil": 5, # Barrier foil：5 ¥/m²  
    "Glass": 5, # Glass：10 ¥/m²  
    "PEDOT:PSS": 6, # PEDOT:PSS：6 ¥/m²  
    "ZnO": 6,  
    "ITO": 125, # ITO：180 ¥/m²  
    "DP3 donor": 15,  # D：0.08g/m²*1500¥/g= 120¥/m²  
    "L8-BO acceptor": 15, # A：0.08g/m²*1500¥/g= 120¥/m²  
    "Solvent": 1, # Solvent：1¥/m²  
    "Ag (top)": 12, # Top Ag electrode：24 ¥/m²  
    "Adhesive": 5,  
}  
result = calculate_msp(  
    material_costs=material_costs_example,  
    pce=0.18,  
    throughput=5.0,  # Doubled coating speed  
    cost_type={  
        'maintenance': 'fixed',    # Maintenance remains fixed  
        'utilities': 'variable',   # Utilities decrease with throughput  
        'labor': 'variable',       # Labor decreases with throughput  
        'depreciation': 'variable'  # Depreciation decreases with throughput  
    }  
)  
# Print results  
print("MSP Results with Throughput Adjustment:")  
for key, value in result.items():  
    print(f"{key}: {value}")  

