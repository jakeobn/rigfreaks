"""
Performance benchmarks module for PC configurations.
Provides benchmark data for different PC components and functionality to estimate performance.
"""
import json
import logging

# CPU Benchmarks (scores based on performance in typical workloads)
CPU_BENCHMARKS = {
    # High-end CPUs
    'ryzen_9_7950x': {
        'single_core': 230,
        'multi_core': 2300,
        'gaming': 210
    },
    'core_i9_13900k': {
        'single_core': 240,
        'multi_core': 2250,
        'gaming': 215
    },
    'ryzen_9_7900x': {
        'single_core': 220,
        'multi_core': 1950,
        'gaming': 205
    },
    'core_i9_12900k': {
        'single_core': 210,
        'multi_core': 1850,
        'gaming': 195
    },
    
    # Mid-range CPUs
    'ryzen_7_7700x': {
        'single_core': 200,
        'multi_core': 1600,
        'gaming': 190
    },
    'core_i7_13700k': {
        'single_core': 215,
        'multi_core': 1800,
        'gaming': 200
    },
    'ryzen_7_5800x': {
        'single_core': 180,
        'multi_core': 1400,
        'gaming': 175
    },
    'core_i7_12700k': {
        'single_core': 195,
        'multi_core': 1600,
        'gaming': 185
    },
    
    # Budget/Entry-level CPUs
    'ryzen_5_7600x': {
        'single_core': 185,
        'multi_core': 1200,
        'gaming': 170
    },
    'core_i5_13600k': {
        'single_core': 190,
        'multi_core': 1350,
        'gaming': 175
    },
    'ryzen_5_5600x': {
        'single_core': 165,
        'multi_core': 1000,
        'gaming': 155
    },
    'core_i5_12600k': {
        'single_core': 175,
        'multi_core': 1150,
        'gaming': 165
    }
}

# GPU Benchmarks (scores based on gaming performance at 1080p, 1440p, and 4K)
GPU_BENCHMARKS = {
    # High-end GPUs
    'rtx_4090': {
        '1080p': 250,
        '1440p': 240,
        '4k': 220,
        'ray_tracing': 230,
        'content_creation': 240
    },
    'rtx_4080': {
        '1080p': 230,
        '1440p': 225,
        '4k': 200,
        'ray_tracing': 210,
        'content_creation': 220
    },
    'rtx_3090': {
        '1080p': 220,
        '1440p': 210,
        '4k': 190,
        'ray_tracing': 190,
        'content_creation': 210
    },
    'rx_7900_xtx': {
        '1080p': 235,
        '1440p': 225,
        '4k': 205,
        'ray_tracing': 180,
        'content_creation': 200
    },
    
    # Mid-range GPUs
    'rtx_4070_ti': {
        '1080p': 215,
        '1440p': 200,
        '4k': 170,
        'ray_tracing': 180,
        'content_creation': 190
    },
    'rtx_3080': {
        '1080p': 210,
        '1440p': 195,
        '4k': 165,
        'ray_tracing': 170,
        'content_creation': 180
    },
    'rx_7900_xt': {
        '1080p': 220,
        '1440p': 210,
        '4k': 180,
        'ray_tracing': 160,
        'content_creation': 185
    },
    'rx_6800_xt': {
        '1080p': 200,
        '1440p': 185,
        '4k': 155,
        'ray_tracing': 140,
        'content_creation': 170
    },
    
    # Budget/Entry-level GPUs
    'rtx_4060_ti': {
        '1080p': 180,
        '1440p': 160,
        '4k': 120,
        'ray_tracing': 150,
        'content_creation': 150
    },
    'rtx_3060_ti': {
        '1080p': 170,
        '1440p': 150,
        '4k': 110,
        'ray_tracing': 130,
        'content_creation': 140
    },
    'rx_6700_xt': {
        '1080p': 175,
        '1440p': 155,
        '4k': 115,
        'ray_tracing': 110,
        'content_creation': 135
    },
    'rx_6600_xt': {
        '1080p': 160,
        '1440p': 135,
        '4k': 95,
        'ray_tracing': 90,
        'content_creation': 120
    }
}

# RAM impact factors (multipliers based on capacity and speed)
RAM_IMPACT = {
    # Capacity impact
    'capacity': {
        64: 1.15,  # 64GB
        32: 1.1,   # 32GB
        16: 1.0,   # 16GB (baseline)
        8: 0.85,   # 8GB
        4: 0.7     # 4GB
    },
    
    # Speed impact
    'speed': {
        6000: 1.15,  # 6000MHz
        5600: 1.1,   # 5600MHz
        5200: 1.05,  # 5200MHz
        4800: 1.03,  # 4800MHz
        4000: 1.0,   # 4000MHz (baseline)
        3600: 0.98,  # 3600MHz
        3200: 0.95,  # 3200MHz
        2933: 0.92,  # 2933MHz
        2666: 0.9,   # 2666MHz
        2400: 0.87   # 2400MHz
    }
}

# Storage impact factors (multipliers based on type and interface)
STORAGE_IMPACT = {
    # Type impact
    'type': {
        'nvme_pcie_4': 1.1,    # NVMe PCIe 4.0
        'nvme_pcie_3': 1.05,   # NVMe PCIe 3.0
        'sata_ssd': 1.0,       # SATA SSD (baseline)
        'hdd_7200': 0.7,       # 7200 RPM HDD
        'hdd_5400': 0.6        # 5400 RPM HDD
    }
}

# Component ID to benchmark mapping
CPU_ID_MAP = {
    'cpu-001': 'ryzen_9_7950x',
    'cpu-002': 'core_i9_13900k',
    'cpu-003': 'ryzen_7_7700x',
    'cpu-004': 'core_i7_13700k',
    'cpu-005': 'ryzen_5_7600x',
    'cpu-006': 'core_i5_13600k',
    'cpu-007': 'ryzen_9_7900x',
    'cpu-008': 'core_i9_12900k',
    'cpu-009': 'ryzen_7_5800x',
    'cpu-010': 'core_i7_12700k',
    'cpu-011': 'ryzen_5_5600x',
    'cpu-012': 'core_i5_12600k',
}

GPU_ID_MAP = {
    'gpu-001': 'rtx_4090',
    'gpu-002': 'rtx_4080',
    'gpu-003': 'rtx_4070_ti',
    'gpu-004': 'rtx_3090',
    'gpu-005': 'rtx_3080',
    'gpu-006': 'rtx_3060_ti',
    'gpu-007': 'rx_7900_xtx',
    'gpu-008': 'rx_7900_xt',
    'gpu-009': 'rx_6800_xt',
    'gpu-010': 'rx_6700_xt',
    'gpu-011': 'rtx_4060_ti',
    'gpu-012': 'rx_6600_xt',
}

# Predefined benchmark categories and their descriptions
BENCHMARK_CATEGORIES = {
    'gaming_1080p': {
        'name': '1080p Gaming',
        'description': 'Performance in games at 1920x1080 resolution',
        'icon': 'fas fa-gamepad'
    },
    'gaming_1440p': {
        'name': '1440p Gaming',
        'description': 'Performance in games at 2560x1440 resolution',
        'icon': 'fas fa-gamepad'
    },
    'gaming_4k': {
        'name': '4K Gaming',
        'description': 'Performance in games at 3840x2160 resolution',
        'icon': 'fas fa-gamepad'
    },
    'content_creation': {
        'name': 'Content Creation',
        'description': 'Performance in video editing, 3D rendering, and other creative workloads',
        'icon': 'fas fa-photo-video'
    },
    'productivity': {
        'name': 'Productivity',
        'description': 'Performance in office applications, web browsing, and multitasking',
        'icon': 'fas fa-laptop-code'
    }
}

# Game benchmarks with estimated FPS based on GPU and CPU combinations
GAME_BENCHMARKS = {
    'cyberpunk_2077': {
        'name': 'Cyberpunk 2077',
        'genre': 'RPG',
        'settings': 'Ultra, RT Off',
        'baseline': {  # RTX 3080 + i7-12700K as baseline
            '1080p': 110,
            '1440p': 85,
            '4k': 45
        },
        'gpu_scaling': {
            'rtx_4090': {'1080p': 1.8, '1440p': 1.9, '4k': 2.2},
            'rtx_4080': {'1080p': 1.6, '1440p': 1.7, '4k': 1.9},
            'rtx_3090': {'1080p': 1.2, '1440p': 1.25, '4k': 1.3},
            'rx_7900_xtx': {'1080p': 1.5, '1440p': 1.6, '4k': 1.7},
            # Other GPUs...
        },
        'cpu_importance': 0.3  # CPU impact weight (1.0 = 100% impact)
    },
    'fortnite': {
        'name': 'Fortnite',
        'genre': 'Battle Royale',
        'settings': 'Epic',
        'baseline': {  # RTX 3080 + i7-12700K as baseline
            '1080p': 180,
            '1440p': 140,
            '4k': 85
        },
        'gpu_scaling': {
            'rtx_4090': {'1080p': 1.5, '1440p': 1.6, '4k': 1.7},
            'rtx_4080': {'1080p': 1.4, '1440p': 1.5, '4k': 1.6},
            'rtx_3090': {'1080p': 1.15, '1440p': 1.2, '4k': 1.25},
            'rx_7900_xtx': {'1080p': 1.35, '1440p': 1.45, '4k': 1.5},
            # Other GPUs...
        },
        'cpu_importance': 0.5  # CPU impact weight (1.0 = 100% impact)
    },
    'call_of_duty_warzone': {
        'name': 'COD: Warzone',
        'genre': 'FPS',
        'settings': 'High',
        'baseline': {  # RTX 3080 + i7-12700K as baseline
            '1080p': 160,
            '1440p': 130,
            '4k': 80
        },
        'gpu_scaling': {
            'rtx_4090': {'1080p': 1.4, '1440p': 1.5, '4k': 1.8},
            'rtx_4080': {'1080p': 1.3, '1440p': 1.4, '4k': 1.6},
            'rtx_3090': {'1080p': 1.1, '1440p': 1.15, '4k': 1.2},
            'rx_7900_xtx': {'1080p': 1.25, '1440p': 1.35, '4k': 1.5},
            # Other GPUs...
        },
        'cpu_importance': 0.6  # CPU impact weight (1.0 = 100% impact)
    }
}

# Application benchmarks for productivity and content creation
APP_BENCHMARKS = {
    'davinci_resolve': {
        'name': 'DaVinci Resolve',
        'category': 'Video Editing',
        'metric': 'Rendering Speed (higher is better)',
        'baseline': 100,  # i7-12700K + RTX 3080 + 32GB RAM
        'cpu_weight': 0.4,
        'gpu_weight': 0.4,
        'ram_weight': 0.2
    },
    'blender': {
        'name': 'Blender',
        'category': '3D Rendering',
        'metric': 'Rendering Time (lower is better)',
        'baseline': 100,  # i7-12700K + RTX 3080 + 32GB RAM
        'cpu_weight': 0.35,
        'gpu_weight': 0.55,
        'ram_weight': 0.1
    },
    'photoshop': {
        'name': 'Adobe Photoshop',
        'category': 'Photo Editing',
        'metric': 'Filter Application Speed (higher is better)',
        'baseline': 100,  # i7-12700K + RTX 3080 + 32GB RAM
        'cpu_weight': 0.6,
        'gpu_weight': 0.25,
        'ram_weight': 0.15
    },
    'premier_pro': {
        'name': 'Adobe Premiere Pro',
        'category': 'Video Editing',
        'metric': 'Export Speed (higher is better)',
        'baseline': 100,  # i7-12700K + RTX 3080 + 32GB RAM
        'cpu_weight': 0.45,
        'gpu_weight': 0.4,
        'ram_weight': 0.15
    }
}


def get_cpu_benchmark(cpu_id):
    """Get CPU benchmark data based on component ID."""
    benchmark_key = CPU_ID_MAP.get(cpu_id)
    if not benchmark_key:
        logging.warning(f"No benchmark data found for CPU ID: {cpu_id}")
        return None
    
    return CPU_BENCHMARKS.get(benchmark_key)


def get_gpu_benchmark(gpu_id):
    """Get GPU benchmark data based on component ID."""
    benchmark_key = GPU_ID_MAP.get(gpu_id)
    if not benchmark_key:
        logging.warning(f"No benchmark data found for GPU ID: {gpu_id}")
        return None
    
    return GPU_BENCHMARKS.get(benchmark_key)


def get_ram_impact(ram_capacity, ram_speed):
    """Calculate RAM impact factor based on capacity and speed."""
    # Find the closest capacity bracket
    capacity_brackets = sorted(RAM_IMPACT['capacity'].keys())
    capacity_bracket = min(capacity_brackets, key=lambda x: abs(x - ram_capacity))
    
    # Find the closest speed bracket
    speed_brackets = sorted(RAM_IMPACT['speed'].keys())
    speed_bracket = min(speed_brackets, key=lambda x: abs(x - ram_speed))
    
    # Multiply the impact factors
    capacity_impact = RAM_IMPACT['capacity'].get(capacity_bracket, 1.0)
    speed_impact = RAM_IMPACT['speed'].get(speed_bracket, 1.0)
    
    return capacity_impact * speed_impact


def get_storage_impact(storage_type):
    """Calculate storage impact factor based on type."""
    return STORAGE_IMPACT['type'].get(storage_type, 1.0)


def calculate_gaming_performance(cpu_id, gpu_id, ram_capacity=16, ram_speed=3200):
    """Calculate gaming performance score for different resolutions."""
    cpu_data = get_cpu_benchmark(cpu_id)
    gpu_data = get_gpu_benchmark(gpu_id)
    
    if not cpu_data or not gpu_data:
        return None
    
    ram_impact = get_ram_impact(ram_capacity, ram_speed)
    
    # Gaming is more GPU dependent but still needs CPU
    performance = {
        '1080p': (gpu_data['1080p'] * 0.7 + cpu_data['gaming'] * 0.3) * ram_impact,
        '1440p': (gpu_data['1440p'] * 0.8 + cpu_data['gaming'] * 0.2) * ram_impact,
        '4k': (gpu_data['4k'] * 0.9 + cpu_data['gaming'] * 0.1) * ram_impact
    }
    
    return performance


def calculate_content_creation_performance(cpu_id, gpu_id, ram_capacity=16, ram_speed=3200):
    """Calculate content creation performance score."""
    cpu_data = get_cpu_benchmark(cpu_id)
    gpu_data = get_gpu_benchmark(gpu_id)
    
    if not cpu_data or not gpu_data:
        return None
    
    ram_impact = get_ram_impact(ram_capacity, ram_speed)
    
    # Content creation uses both CPU and GPU heavily
    performance = (
        cpu_data['multi_core'] * 0.5 + 
        gpu_data['content_creation'] * 0.4 + 
        cpu_data['single_core'] * 0.1
    ) * ram_impact
    
    return performance


def calculate_productivity_performance(cpu_id, gpu_id, ram_capacity=16, ram_speed=3200):
    """Calculate productivity performance score."""
    cpu_data = get_cpu_benchmark(cpu_id)
    
    if not cpu_data:
        return None
    
    ram_impact = get_ram_impact(ram_capacity, ram_speed)
    
    # Productivity is mostly CPU dependent with emphasis on single-core
    performance = (
        cpu_data['single_core'] * 0.6 + 
        cpu_data['multi_core'] * 0.4
    ) * ram_impact
    
    return performance


def calculate_game_fps(cpu_id, gpu_id, game_id, resolution='1080p', ram_capacity=16, ram_speed=3200):
    """Calculate estimated FPS for a specific game."""
    game_data = GAME_BENCHMARKS.get(game_id)
    if not game_data:
        logging.warning(f"No benchmark data found for game: {game_id}")
        return None
    
    # Get component benchmark data
    gpu_key = GPU_ID_MAP.get(gpu_id)
    cpu_data = get_cpu_benchmark(cpu_id)
    
    if not gpu_key or not cpu_data:
        return None
    
    # Get baseline FPS for the resolution
    baseline_fps = game_data['baseline'].get(resolution, 60)
    
    # Get GPU scaling factor
    gpu_scaling = game_data['gpu_scaling'].get(gpu_key, {}).get(resolution, 1.0)
    
    # Calculate CPU impact
    cpu_impact = 1.0
    if game_data['cpu_importance'] > 0:
        # Compare to a reference CPU (i7-12700K)
        ref_cpu = CPU_BENCHMARKS.get('core_i7_12700k', {}).get('gaming', 185)
        if ref_cpu > 0:
            cpu_factor = cpu_data['gaming'] / ref_cpu
            # Apply CPU importance factor
            cpu_impact = 1.0 + (cpu_factor - 1.0) * game_data['cpu_importance']
    
    # Apply RAM impact
    ram_impact = get_ram_impact(ram_capacity, ram_speed)
    
    # Calculate final FPS
    return round(baseline_fps * gpu_scaling * cpu_impact * ram_impact)


def calculate_app_performance(cpu_id, gpu_id, app_id, ram_capacity=16, ram_speed=3200):
    """Calculate performance score for a specific application."""
    app_data = APP_BENCHMARKS.get(app_id)
    if not app_data:
        logging.warning(f"No benchmark data found for application: {app_id}")
        return None
    
    # Get component benchmark data
    cpu_data = get_cpu_benchmark(cpu_id)
    gpu_data = get_gpu_benchmark(gpu_id)
    
    if not cpu_data or not gpu_data:
        return None
    
    # Calculate RAM impact
    ram_impact = get_ram_impact(ram_capacity, ram_speed)
    
    # Compare to reference components
    ref_cpu_multi = CPU_BENCHMARKS.get('core_i7_12700k', {}).get('multi_core', 1600)
    ref_gpu_content = GPU_BENCHMARKS.get('rtx_3080', {}).get('content_creation', 180)
    
    cpu_factor = cpu_data['multi_core'] / ref_cpu_multi if ref_cpu_multi > 0 else 1.0
    gpu_factor = gpu_data['content_creation'] / ref_gpu_content if ref_gpu_content > 0 else 1.0
    
    # Combine factors with weights
    performance = (
        cpu_factor * app_data['cpu_weight'] +
        gpu_factor * app_data['gpu_weight'] +
        ram_impact * app_data['ram_weight']
    ) * app_data['baseline']
    
    return round(performance)


def get_performance_score(config):
    """Calculate overall performance scores for a PC configuration."""
    if not config or 'cpu' not in config or 'gpu' not in config:
        return None
    
    cpu_id = config.get('cpu')
    gpu_id = config.get('gpu')
    
    # Extract RAM details if available
    ram_capacity = 16  # Default
    ram_speed = 3200  # Default
    
    if 'ram' in config:
        # In a real implementation, you would look up the RAM details from the database
        # For now, we'll use placeholder values based on price points
        ram_id = config.get('ram')
        if ram_id.startswith('ram-00'):
            ram_capacity = 32
            ram_speed = 4000
        elif ram_id.startswith('ram-01'):
            ram_capacity = 16
            ram_speed = 3600
        else:
            ram_capacity = 8
            ram_speed = 3200
    
    # Calculate performance scores
    gaming_perf = calculate_gaming_performance(cpu_id, gpu_id, ram_capacity, ram_speed)
    content_perf = calculate_content_creation_performance(cpu_id, gpu_id, ram_capacity, ram_speed)
    productivity_perf = calculate_productivity_performance(cpu_id, gpu_id, ram_capacity, ram_speed)
    
    # Selected game benchmarks
    game_fps = {
        'cyberpunk_2077': {
            '1080p': calculate_game_fps(cpu_id, gpu_id, 'cyberpunk_2077', '1080p', ram_capacity, ram_speed),
            '1440p': calculate_game_fps(cpu_id, gpu_id, 'cyberpunk_2077', '1440p', ram_capacity, ram_speed),
            '4k': calculate_game_fps(cpu_id, gpu_id, 'cyberpunk_2077', '4k', ram_capacity, ram_speed)
        },
        'fortnite': {
            '1080p': calculate_game_fps(cpu_id, gpu_id, 'fortnite', '1080p', ram_capacity, ram_speed),
            '1440p': calculate_game_fps(cpu_id, gpu_id, 'fortnite', '1440p', ram_capacity, ram_speed),
            '4k': calculate_game_fps(cpu_id, gpu_id, 'fortnite', '4k', ram_capacity, ram_speed)
        },
        'call_of_duty_warzone': {
            '1080p': calculate_game_fps(cpu_id, gpu_id, 'call_of_duty_warzone', '1080p', ram_capacity, ram_speed),
            '1440p': calculate_game_fps(cpu_id, gpu_id, 'call_of_duty_warzone', '1440p', ram_capacity, ram_speed),
            '4k': calculate_game_fps(cpu_id, gpu_id, 'call_of_duty_warzone', '4k', ram_capacity, ram_speed)
        }
    }
    
    # Selected application benchmarks
    app_scores = {
        'davinci_resolve': calculate_app_performance(cpu_id, gpu_id, 'davinci_resolve', ram_capacity, ram_speed),
        'blender': calculate_app_performance(cpu_id, gpu_id, 'blender', ram_capacity, ram_speed),
        'photoshop': calculate_app_performance(cpu_id, gpu_id, 'photoshop', ram_capacity, ram_speed),
        'premier_pro': calculate_app_performance(cpu_id, gpu_id, 'premier_pro', ram_capacity, ram_speed)
    }
    
    return {
        'gaming': gaming_perf,
        'content_creation': content_perf,
        'productivity': productivity_perf,
        'games': game_fps,
        'applications': app_scores
    }


def get_performance_summary(config):
    """Get a simplified summary of performance scores."""
    scores = get_performance_score(config)
    if not scores:
        return None
    
    # Extract key metrics for summary
    summary = {}
    
    # Gaming performance
    if scores['gaming']:
        summary['gaming_1080p'] = round(scores['gaming']['1080p'])
        summary['gaming_1440p'] = round(scores['gaming']['1440p'])
        summary['gaming_4k'] = round(scores['gaming']['4k'])
    
    # Content creation and productivity
    if scores['content_creation']:
        summary['content_creation'] = round(scores['content_creation'])
    
    if scores['productivity']:
        summary['productivity'] = round(scores['productivity'])
    
    # Performance tier classification
    tiers = ['Entry-level', 'Mainstream', 'High-end', 'Enthusiast', 'Ultimate']
    
    # Determine overall tier based on gaming performance at 1080p
    if summary.get('gaming_1080p', 0) < 130:
        summary['tier'] = tiers[0]
    elif summary.get('gaming_1080p', 0) < 160:
        summary['tier'] = tiers[1]
    elif summary.get('gaming_1080p', 0) < 190:
        summary['tier'] = tiers[2]
    elif summary.get('gaming_1080p', 0) < 220:
        summary['tier'] = tiers[3]
    else:
        summary['tier'] = tiers[4]
    
    # Add game FPS for popular games
    if scores['games']:
        summary['game_fps'] = {
            'cyberpunk_2077_1080p': scores['games']['cyberpunk_2077']['1080p'],
            'fortnite_1080p': scores['games']['fortnite']['1080p'],
            'cod_warzone_1080p': scores['games']['call_of_duty_warzone']['1080p']
        }
    
    return summary


def get_comparison_data(config1, config2=None):
    """Compare performance between two configurations."""
    score1 = get_performance_score(config1)
    
    if not config2:
        # Compare against reference configurations
        reference_configs = {
            'budget': {
                'cpu': 'cpu-011',  # ryzen_5_5600x
                'gpu': 'gpu-012',  # rx_6600_xt
                'ram': 'ram-015'   # 8GB DDR4-3200
            },
            'mid_range': {
                'cpu': 'cpu-004',  # core_i7_13700k
                'gpu': 'gpu-006',  # rtx_3060_ti
                'ram': 'ram-010'   # 16GB DDR4-3600
            },
            'high_end': {
                'cpu': 'cpu-002',  # core_i9_13900k
                'gpu': 'gpu-002',  # rtx_4080
                'ram': 'ram-005'   # 32GB DDR5-6000
            }
        }
        
        comparisons = {}
        for tier, ref_config in reference_configs.items():
            ref_score = get_performance_score(ref_config)
            if ref_score and score1:
                comparisons[tier] = {
                    'gaming_1080p': round((score1['gaming']['1080p'] / ref_score['gaming']['1080p']) * 100),
                    'gaming_4k': round((score1['gaming']['4k'] / ref_score['gaming']['4k']) * 100),
                    'content_creation': round((score1['content_creation'] / ref_score['content_creation']) * 100),
                    'productivity': round((score1['productivity'] / ref_score['productivity']) * 100)
                }
        
        return comparisons
    
    # Compare with another configuration
    score2 = get_performance_score(config2)
    
    if not score1 or not score2:
        return None
    
    comparison = {
        'gaming_1080p': round((score1['gaming']['1080p'] / score2['gaming']['1080p']) * 100),
        'gaming_1440p': round((score1['gaming']['1440p'] / score2['gaming']['1440p']) * 100),
        'gaming_4k': round((score1['gaming']['4k'] / score2['gaming']['4k']) * 100),
        'content_creation': round((score1['content_creation'] / score2['content_creation']) * 100),
        'productivity': round((score1['productivity'] / score2['productivity']) * 100)
    }
    
    return comparison