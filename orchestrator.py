import asyncio
import importlib
import os
from datetime import datetime

from utils.file_processor import FileProcessor
from agents.agent_manager import AgentManager
from agents.job_search_agent import JobSearchAgent


class DynamicFeatureStub:
    def __init__(self, feature_name, methods=None):
        self.feature_name = feature_name
        self.methods = methods or []

    def __getattr__(self, name):
        def stub(*args, **kwargs):
            return {'status': 'stub', 'feature': self.feature_name}
        return stub


class FastOrchestrator:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.file_processor = FileProcessor()
        self.job_search_agent = JobSearchAgent()
        self.features = self._load_features()

    def _load_features(self):
        feature_config = {
            'ab_testing':         ('ABTestingAgent',          ['generate_variants']),
            'company_research':   ('CompanyResearchAgent',    ['analyze_company']),
            'culture_fit_analyzer':('CultureFitAnalyzer',    ['analyze_fit']),
            'global_optimizer':   ('GlobalOptimizer',         ['optimize_for_international']),
            'industry_specialist':('IndustrySpecialist',      ['analyze_industry_fit']),
            'interactive_builder':('InteractiveBuilder',      ['get_improvement_suggestions']),
            'interview_prep':     ('InterviewPrepAgent',      ['generate_questions']),
            'learning_path':      ('LearningPathAgent',       ['generate_learning_plan']),
            'market_intelligence':('MarketIntelligenceAgent', ['get_market_insights']),
            'mobile_optimizer':   ('MobileOptimizer',         ['analyze_mobile_compatibility']),
            'networking_engine':  ('NetworkingEngine',        ['generate_networking_strategy']),
            'resume_health_track':('ResumeHealthTracker',     ['track_health_metrics']),
            'storytelling_agent': ('StorytellingAgent',       ['craft_career_narrative']),
            'visual_analytics':   ('VisualAnalytics',         ['generate_analytics']),
            'resume_comparison':  ('ResumeComparison',        ['generate_comparison']),
        }
        feats = {}
        for name, (cls_name, methods) in feature_config.items():
            try:
                module = importlib.import_module(f'features.{name}')
                cls = getattr(module, cls_name)
                feats[name] = cls()
            except Exception as e:
                print(f"⚠️  Feature '{name}' failed to load: {e}")
                feats[name] = DynamicFeatureStub(name, methods)
        return feats

    # ------------------------------------------------------------------ #
    #  Main entry point
    # ------------------------------------------------------------------ #

    async def process_resume(self, file_path, job_description, target_role, location):
        try:
            resume_text = self.file_processor.extract_text(file_path)

            # ── Core pipeline ──────────────────────────────────────────
            core = await self.agent_manager.optimize_resume(
                resume_text, job_description, target_role, location
            )

            # Normalise core output — never let an error string propagate
            if isinstance(core, str):
                # The agent returned a raw string (possibly an error message)
                is_error = any(
                    phrase in core.lower()
                    for phrase in ['error', 'failed', 'exception', 'encountered an error']
                )
                core = {
                    'optimized_resume':      resume_text if is_error else core,
                    'final_score':           {'overall_score': 0, 'confidence_level': 'low'},
                    'improvement_percentage': 0,
                    'jd_analysis':           {},
                    'critique':              {},
                    'gap_analysis':          {},
                }

            # Make sure optimized_resume is always a usable string
            optimized_resume = core.get('optimized_resume', '').strip()
            if not optimized_resume or _looks_like_error(optimized_resume):
                print("⚠️  optimized_resume looks like an error — using original resume")
                optimized_resume = resume_text
                core['optimized_resume'] = resume_text

            # ── Feature pipeline ───────────────────────────────────────
            feature_results = await self._run_features(
                resume_text, optimized_resume, job_description, target_role, location
            )

            # ── Job search ─────────────────────────────────────────────
            jobs = await self._get_jobs(target_role, location)

            return {
                **core,
                **feature_results,
                'job_listings': jobs,
                'processing_metadata': {
                    'timestamp':      datetime.utcnow().isoformat(),
                    'features_count': len(feature_results),
                    'jobs_found':     len(jobs),
                },
            }

        except Exception as e:
            print(f"❌ FastOrchestrator.process_resume failed: {e}")
            return self._fallback(str(e))

    # ------------------------------------------------------------------ #
    #  Feature runner
    # ------------------------------------------------------------------ #

    async def _run_features(self, orig, opt, jd, role, loc):
        """
        Run every feature concurrently. Each result is validated before
        being included — exceptions and error-string results are dropped
        so they never pollute the comparison view.
        """
        method_map = {
            'resume_comparison':  (['generate_comparison'], [orig, opt, jd]),
            'learning_path':      (['generate_learning_plan'], [opt, role]),
            'interview_prep':     (['generate_questions'], [opt, jd]),
            'company_research':   (['analyze_company'], [jd, role]),
            'culture_fit_analyzer':(['analyze_fit'], [opt, jd]),
            'market_intelligence':(['get_market_insights'], [jd, role]),
            'networking_engine':  (['generate_networking_strategy'], [opt, role, loc]),
            'storytelling_agent': (['craft_career_narrative'], [opt, role]),
            'visual_analytics':   (['generate_analytics'], [orig, opt, jd]),
            'resume_health_track':(['track_health_metrics'], [opt]),
            'ab_testing':         (['generate_variants'], [opt, jd]),
            'industry_specialist':(['analyze_industry_fit'], [opt, jd, role]),
            'global_optimizer':   (['optimize_for_international'], [opt, role, loc]),
            'mobile_optimizer':   (['analyze_mobile_compatibility'], [opt]),
            'interactive_builder':(['get_improvement_suggestions'], [opt, jd]),
        }

        tasks   = []
        ordered = []  # track which feature each task belongs to

        for fname, (methods, args) in method_map.items():
            feat = self.features.get(fname)
            if not feat:
                continue
            for m in methods:
                if hasattr(feat, m):
                    method = getattr(feat, m)
                    if asyncio.iscoroutinefunction(method):
                        tasks.append(method(*args))
                    else:
                        tasks.append(asyncio.to_thread(method, *args))
                    ordered.append(fname)
                    break

        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        output = {}
        for fname, res in zip(ordered, raw_results):
            if isinstance(res, Exception):
                print(f"⚠️  Feature '{fname}' raised: {res}")
                continue
            # Drop results that are error-string dicts
            if isinstance(res, dict) and _looks_like_error(str(res.get('status', ''))):
                continue
            output[fname] = res

        return output

    # ------------------------------------------------------------------ #
    #  Job search
    # ------------------------------------------------------------------ #

    async def _get_jobs(self, target_role, location):
        if not target_role:
            return []
        try:
            jobs = await self.job_search_agent.search_real_jobs(target_role, location)
            return jobs or []
        except Exception as e:
            print(f"⚠️  Job search failed: {e}")
            return []

    # ------------------------------------------------------------------ #
    #  Fallback
    # ------------------------------------------------------------------ #

    def _fallback(self, error_msg):
        return {
            'error':                 error_msg,
            'optimized_resume':      '',
            'final_score':           {'overall_score': 0, 'confidence_level': 'low'},
            'improvement_percentage': 0,
            'jd_analysis':           {},
            'critique':              {},
            'gap_analysis':          {},
            'job_listings':          [],
        }


# ------------------------------------------------------------------ #
#  Helper
# ------------------------------------------------------------------ #

def _looks_like_error(text: str) -> bool:
    """Return True if a string looks like an error message rather than content."""
    if not text:
        return True
    error_phrases = [
        'encountered an error',
        'optimisation encountered',
        'optimization encountered',
        'failed',
        'exception',
        'traceback',
        'error:',
    ]
    lower = text.lower().strip()
    return any(lower.startswith(p) or lower == p for p in error_phrases)