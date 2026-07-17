"""Compatibility entrypoint for the reasoning-chain factory / 推理链工厂兼容入口。

Static compilation and validation live in reasoning_chain_compiler; guarded
runtime execution lives in reasoning_chain_session. Existing imports continue
to work through this intentionally small facade. / 静态编译与校验位于
reasoning_chain_compiler，受守卫运行执行位于 reasoning_chain_session；现有导入
继续通过本兼容门面工作。
"""

try:  # Package import / 包导入
    from .reasoning_chain_compiler import (
        ChainFactoryError,
        ChainPlanDriftError,
        ChainPlanStateError,
        FACTORY_ID,
        FACTORY_VERSION,
        PLAN_VERSION,
        ReasoningChainFactory,
        validate_chain_blueprint,
        validate_chain_plan,
    )
    from .reasoning_chain_session import ChainPlanSession, ChainStepOutcome
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_chain_compiler import (
        ChainFactoryError,
        ChainPlanDriftError,
        ChainPlanStateError,
        FACTORY_ID,
        FACTORY_VERSION,
        PLAN_VERSION,
        ReasoningChainFactory,
        validate_chain_blueprint,
        validate_chain_plan,
    )
    from reasoning_chain_session import ChainPlanSession, ChainStepOutcome

__all__ = [
    "ChainFactoryError",
    "ChainPlanDriftError",
    "ChainPlanSession",
    "ChainPlanStateError",
    "ChainStepOutcome",
    "FACTORY_ID",
    "FACTORY_VERSION",
    "PLAN_VERSION",
    "ReasoningChainFactory",
    "validate_chain_blueprint",
    "validate_chain_plan",
]
