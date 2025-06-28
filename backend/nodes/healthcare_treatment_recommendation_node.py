from adapters.local_model_adapter import LocalModelAdapter
from typing import Dict, Any, List, Optional
import googlemaps
import asyncio
import re
from functools import lru_cache
import hashlib

class HealthcareRecommendationNode:
    def __init__(self, adapter: LocalModelAdapter, google_maps_api_key: Optional[str] = None):
        self.adapter = adapter
        self.gmaps_client = googlemaps.Client(key=google_maps_api_key) if google_maps_api_key else None
        
        # ✅ Smart keyword-based mapping (no fixed types!)
        self.specialist_keywords = {
            # Cardiovascular
            "heart": ["cardiology", "cardiac", "heart center"],
            "cardiac": ["cardiology", "heart specialist", "cardiac center"],
            "chest": ["cardiology", "chest pain clinic"],
            "interventional": ["interventional cardiology", "cardiac catheterization"],
            
            # Dermatology
            "skin": ["dermatology", "skin specialist", "dermatologist"],
            "dermatolog": ["dermatology clinic", "skin center"],
            "mole": ["dermatology", "mole clinic", "skin cancer"],
            "rash": ["dermatology", "skin clinic"],
            "lesion": ["dermatology", "skin lesion clinic"],
            
            # Neurology
            "neuro": ["neurology", "brain specialist", "neurologist"],
            "brain": ["neurology clinic", "neuroscience center"],
            "headache": ["neurology", "headache clinic"],
            "migraine": ["neurology", "migraine center"],
            
            # Orthopedic
            "bone": ["orthopedic", "bone specialist", "orthopedics"],
            "joint": ["orthopedic", "joint clinic", "arthritis center"],
            "fracture": ["orthopedic", "trauma center"],
            "spine": ["spine clinic", "orthopedic spine"],
            
            # Eye care
            "eye": ["ophthalmology", "eye clinic", "vision center"],
            "vision": ["ophthalmology", "optometry"],
            "retina": ["retinal specialist", "ophthalmology"],
            
            # ENT
            "ear": ["ENT", "otolaryngology", "ear nose throat"],
            "throat": ["ENT clinic", "otolaryngology"],
            "sinus": ["ENT", "sinus center"],
            
            # Mental health
            "mental": ["psychiatry", "mental health", "behavioral health"],
            "depression": ["psychiatry", "mental health clinic"],
            "anxiety": ["psychiatry", "anxiety clinic"],
            "behavioral": ["behavioral health", "psychology"],
            
            # Specialized
            "cancer": ["oncology", "cancer center", "hematology oncology"],
            "tumor": ["oncology clinic", "cancer treatment"],
            "kidney": ["nephrology", "kidney specialist"],
            "liver": ["hepatology", "gastroenterology", "liver clinic"],
            "lung": ["pulmonology", "lung specialist", "respiratory"],
            "diabetes": ["endocrinology", "diabetes center"],
            "thyroid": ["endocrinology", "thyroid clinic"],
            "infectious": ["infectious disease", "ID clinic"],
            "pain": ["pain management", "pain clinic"],
            "emergency": ["emergency room", "urgent care", "ER"],
            "urgent": ["urgent care", "immediate care"],
            
            # Pediatric
            "pediatric": ["pediatric", "children's hospital", "pediatrics"],
            "child": ["pediatric clinic", "children's health"],
            
            # Women's health
            "gynecol": ["gynecology", "women's health"],
            "obstetric": ["obstetrics", "maternal health"],
            "reproductive": ["reproductive health", "fertility clinic"],
            
            # Urology
            "urinary": ["urology", "urologist"],
            "prostate": ["urology", "men's health"],
            "bladder": ["urology clinic", "urologist"]
        }
        
        # Dynamic urgency-based search radius
        self.urgency_radius = {
            "immediate": 10000,    # 10km for immediate care
            "within_week": 25000,  # 25km for week timeline
            "within_month": 50000, # 50km for month timeline
            "emergency": 15000     # 15km for emergency
        }
        
        # Cache for performance
        self._facility_cache = {}
        self._advice_cache = {}
        
    async def __call__(self, state):
        print("🏥 HEALTHCARE RECOMMENDATION NODE CALLED!")
        
        # Set stage when node starts
        state["current_workflow_stage"] = "healthcare_recommendation"
        
        state = await self.generate_healthcare_recommendation(state)
        
        state["current_workflow_stage"] = "healthcare_recommendation_complete"
        return state
    
    async def generate_healthcare_recommendation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced healthcare recommendations with maximum flexibility"""
        
        try:
            # Get overall analysis results
            overall_analysis = state.get("overall_analysis", {})
            
            if not overall_analysis:
                state["healthcare_recommendation"] = self._get_default_recommendation()
                return state
            
            # Extract key information
            diagnosis = overall_analysis.get("final_diagnosis", "Unknown")
            severity = overall_analysis.get("final_severity", "moderate").lower()
            confidence = overall_analysis.get("final_confidence", 0.0)
            specialist_recommendation = overall_analysis.get("specialist_recommendation", "general practitioner")
            
            # Determine recommendation type and urgency
            recommendation_type, urgency = self._determine_recommendation_and_urgency(
                diagnosis, severity, confidence, specialist_recommendation
            )
            
            print(f"🎯 Recommendation: {recommendation_type} | Urgency: {urgency}")
            print(f"🏥 Specialist needed: {specialist_recommendation}")
            
            # Initialize comprehensive recommendation structure
            recommendation = {
                "recommendation_type": recommendation_type,
                "specialist_type": specialist_recommendation,  # ✅ Free-form specialist
                "appointment_urgency": urgency,
                "self_care_advice": None,
                "nearby_facilities": None,
                "facility_search_radius": None,
                "emergency_contacts": None,
                "insurance_guidance": None,
                "rag_evidence": None,
                "telemedicine_options": None,
                "cost_estimates": None
            }
            
            # Execute parallel tasks based on recommendation type
            tasks = []
            
            if recommendation_type == "self_care":
                tasks.extend([
                    self._generate_self_care_advice(diagnosis, severity),
                    self._get_telemedicine_options(specialist_recommendation),
                    self._generate_cost_estimates("self_care", specialist_recommendation)
                ])
                
            elif recommendation_type == "see_specialist":
                tasks.extend([
                    self._find_any_specialist_facilities(state, specialist_recommendation, urgency),
                    self._generate_insurance_guidance(specialist_recommendation, urgency),
                    self._get_rag_evidence(diagnosis),
                    self._get_telemedicine_options(specialist_recommendation),
                    self._generate_cost_estimates("specialist", specialist_recommendation)
                ])
                
            elif recommendation_type == "emergency_care":
                tasks.extend([
                    self._find_emergency_facilities(state),
                    self._get_emergency_contacts(state),
                    self._get_rag_evidence(diagnosis),
                    self._generate_cost_estimates("emergency", specialist_recommendation)
                ])
            
            # Execute all tasks in parallel for maximum performance
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results based on recommendation type
                if recommendation_type == "self_care":
                    recommendation["self_care_advice"] = self._safe_result(results, 0, [])
                    recommendation["telemedicine_options"] = self._safe_result(results, 1, [])
                    recommendation["cost_estimates"] = self._safe_result(results, 2, {})
                    
                elif recommendation_type == "see_specialist":
                    recommendation["nearby_facilities"] = self._safe_result(results, 0, [])
                    recommendation["insurance_guidance"] = self._safe_result(results, 1, [])
                    recommendation["rag_evidence"] = self._safe_result(results, 2, [])
                    recommendation["telemedicine_options"] = self._safe_result(results, 3, [])
                    recommendation["cost_estimates"] = self._safe_result(results, 4, {})
                    recommendation["facility_search_radius"] = self._get_search_radius_text(urgency)
                    
                elif recommendation_type == "emergency_care":
                    recommendation["nearby_facilities"] = self._safe_result(results, 0, [])
                    recommendation["emergency_contacts"] = self._safe_result(results, 1, [])
                    recommendation["rag_evidence"] = self._safe_result(results, 2, [])
                    recommendation["cost_estimates"] = self._safe_result(results, 3, {})
                    recommendation["facility_search_radius"] = "15km (emergency radius)"
            
            state["healthcare_recommendation"] = recommendation
            state["current_workflow_stage"] = "generating_report"
            
            print(f"✅ Healthcare recommendation generated successfully")
            
        except Exception as e:
            print(f"❌ Healthcare recommendation failed: {e}")
            state["healthcare_recommendation"] = self._get_default_recommendation()
            state["current_workflow_stage"] = "generating_report"
        
        return state
    
    def _safe_result(self, results: List, index: int, default: Any) -> Any:
        """Safely extract result from parallel task execution"""
        try:
            if index < len(results) and not isinstance(results[index], Exception):
                return results[index]
        except (IndexError, TypeError):
            pass
        return default
    
    def _determine_recommendation_and_urgency(self, diagnosis: str, severity: str, confidence: float, specialist_type: str) -> tuple:
        """Enhanced recommendation logic with flexible specialist handling"""
        
        diagnosis_lower = diagnosis.lower()
        specialist_lower = specialist_type.lower()
        
        # Emergency conditions (keyword-based)
        emergency_keywords = [
            "heart attack", "myocardial infarction", "stroke", "severe bleeding", 
            "difficulty breathing", "chest pain", "severe injury", "unconscious", 
            "seizure", "anaphylaxis", "severe trauma", "cardiac arrest"
        ]
        
        if any(keyword in diagnosis_lower for keyword in emergency_keywords) or severity == "emergency":
            return "emergency_care", "immediate"
        
        # Emergency specialist indicators
        emergency_specialists = ["emergency", "trauma", "critical care", "intensive care"]
        if any(spec in specialist_lower for spec in emergency_specialists):
            return "emergency_care", "immediate"
        
        # Critical severity
        if severity == "critical":
            return "see_specialist", "immediate"
        
        # Severe conditions
        if severity == "severe":
            return "see_specialist", "within_week"
        
        # Moderate conditions with specialist recommendation
        if severity == "moderate":
            if confidence >= 0.7:
                return "see_specialist", "within_week"
            else:
                return "see_specialist", "within_month"
        
        # Mild conditions - but some may still need specialist
        if severity == "mild":
            # Check if specialist is specifically mentioned
            if "specialist" in specialist_lower or any(
                keyword in specialist_lower for keyword in 
                ["oncologist", "cardiologist", "neurologist", "dermatologist"]
            ):
                return "see_specialist", "within_month"
            else:
                return "self_care", "within_month"
        
        # Default based on confidence and specialist type
        if confidence < 0.4 or "specialist" in specialist_lower:
            return "see_specialist", "within_month"
        
        return "self_care", "within_month"
    
    def _extract_search_terms_from_specialist(self, specialist_text: str) -> List[str]:
        """Smart extraction of search terms from any specialist description"""
        
        specialist_lower = specialist_text.lower()
        search_terms = set()
        
        # Check for keyword matches
        for keyword, terms in self.specialist_keywords.items():
            if keyword in specialist_lower:
                search_terms.update(terms)
        
        # Extract individual words that might be specialties
        words = re.findall(r'\b\w+\b', specialist_lower)
        for word in words:
            if len(word) > 4:  # Skip short words
                search_terms.add(f"{word} clinic")
                search_terms.add(f"{word} specialist")
        
        # Add the full specialist text as search term
        search_terms.add(specialist_text)
        search_terms.add(f"{specialist_text} clinic")
        
        # Generic fallbacks
        search_terms.update(["medical center", "clinic", "hospital", "healthcare"])
        
        # Convert to list and limit
        return list(search_terms)[:5]  # Top 5 search terms
    
    async def _find_any_specialist_facilities(self, state: Dict[str, Any], specialist_text: str, urgency: str) -> List[Dict[str, Any]]:
        """Find facilities for ANY specialist type using intelligent keyword extraction"""
        
        if not self.gmaps_client or not state.get("user_location"):
            return []
        
        location = state["user_location"]
        radius = self.urgency_radius.get(urgency, 25000)
        search_terms = self._extract_search_terms_from_specialist(specialist_text)
        
        facilities = []
        cache_key = f"{location['lat']},{location['lng']},{specialist_text},{urgency}"
        
        # Check cache first
        if cache_key in self._facility_cache:
            return self._facility_cache[cache_key]
        
        try:
            # Search with multiple terms for comprehensive results
            for search_term in search_terms[:3]:  # Limit for performance
                places_result = self.gmaps_client.places_nearby(
                    location=(location["lat"], location["lng"]),
                    radius=radius,
                    keyword=search_term,
                    type="hospital"
                )
                
                for place in places_result.get("results", [])[:3]:  # Top 3 per search
                    place_details = self._extract_place_details(place, location)
                    
                    # Avoid duplicates
                    if not any(f["place_id"] == place_details["place_id"] for f in facilities):
                        facilities.append(place_details)
            
            # Sort by rating and distance
            facilities.sort(key=lambda x: (-x.get("rating", 0), x.get("distance_km", 999)))
            
            # Cache the results
            result = facilities[:5]  # Return top 5
            self._facility_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            print(f"❌ Google Maps search failed for '{specialist_text}': {e}")
            return []
    
    async def _find_emergency_facilities(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find nearest emergency facilities"""
        
        if not self.gmaps_client or not state.get("user_location"):
            return []
        
        location = state["user_location"]
        
        try:
            places_result = self.gmaps_client.places_nearby(
                location=(location["lat"], location["lng"]),
                radius=15000,  # 15km for emergency
                keyword="emergency room",
                type="hospital"
            )
            
            facilities = []
            for place in places_result.get("results", [])[:5]:
                facility = self._extract_place_details(place, location)
                facility["facility_type"] = "emergency_room"
                facility["emergency_services"] = True
                facilities.append(facility)
            
            return facilities
            
        except Exception:
            return []
    
    def _extract_place_details(self, place: Dict, user_location: Dict) -> Dict[str, Any]:
        """Extract detailed information from Google Places result"""
        
        place_location = place.get("geometry", {}).get("location", {})
        distance_km = self._calculate_distance(user_location, place_location)
        
        return {
            "place_id": place.get("place_id", ""),
            "name": place.get("name", "Unknown"),
            "address": place.get("vicinity", "Address not available"),
            "rating": place.get("rating", 0),
            "total_ratings": place.get("user_ratings_total", 0),
            "price_level": place.get("price_level", None),
            "phone": place.get("formatted_phone_number", ""),
            "website": place.get("website", ""),
            "opening_hours": self._extract_opening_hours(place),
            "distance_km": distance_km,
            "distance_text": f"{distance_km:.1f}km" if distance_km < 1 else f"{int(distance_km)}km",
            "google_maps_url": f"https://maps.google.com/?place_id={place.get('place_id', '')}",
            "types": place.get("types", []),
            "business_status": place.get("business_status", "OPERATIONAL")
        }
    
    def _extract_opening_hours(self, place: Dict) -> Dict[str, Any]:
        """Extract opening hours information"""
        opening_hours = place.get("opening_hours", {})
        
        return {
            "open_now": opening_hours.get("open_now", None),
            "periods": opening_hours.get("periods", []),
            "weekday_text": opening_hours.get("weekday_text", [])
        }
    
    async def _generate_self_care_advice(self, diagnosis: str, severity: str) -> List[str]:
        """Generate intelligent self-care advice"""
        
        cache_key = f"self_care_{diagnosis}_{severity}"
        if cache_key in self._advice_cache:
            return self._advice_cache[cache_key]
        
        try:
            prompt = f"""
            Generate 5-7 practical self-care recommendations for:
            Diagnosis: {diagnosis}
            Severity: {severity}
            
            Focus on:
            1. Immediate symptom relief
            2. Home treatment options
            3. When to seek medical attention
            4. Lifestyle modifications
            5. Warning signs to watch for
            
            Keep advice practical, safe, and actionable.
            """
            
            response = await self.adapter.run_sync(
                self.adapter._generate_text_sync, prompt, 300, 0.3
            )
            
            # Parse advice into list
            advice = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or 
                           (len(line) > 0 and line[0].isdigit())):
                    clean_advice = re.sub(r'^[-•0-9.\s]+', '', line).strip()
                    if clean_advice:
                        advice.append(clean_advice)
            
            # Cache the result
            self._advice_cache[cache_key] = advice
            return advice
            
        except Exception:
            # Fallback advice
            return [
                "Monitor symptoms closely",
                "Rest and stay hydrated",
                "Take over-the-counter medications as needed",
                "Seek medical attention if symptoms worsen",
                "Follow up with healthcare provider as recommended"
            ]
    
    async def _generate_insurance_guidance(self, specialist_type: str, urgency: str) -> List[str]:
        """Generate comprehensive insurance guidance"""
        
        guidance = [
            f"Contact your insurance provider to verify coverage for {specialist_type}",
            "Ask about in-network providers to minimize out-of-pocket costs",
            "Inquire about referral requirements from your primary care doctor"
        ]
        
        if urgency == "immediate":
            guidance.extend([
                "Emergency care is typically covered regardless of network status",
                "Keep all receipts and documentation for insurance claims",
                "Ask hospital about financial assistance programs if needed"
            ])
        else:
            guidance.extend([
                "Schedule during your insurance plan year to maximize benefits",
                "Ask about payment plans if costs are a concern",
                "Consider getting a second opinion if treatment is complex"
            ])
        
        # Add specialist-specific guidance
        if "specialist" in specialist_type.lower():
            guidance.append("Specialist consultations may require higher copayments")
        
        return guidance
    
    async def _get_emergency_contacts(self, state: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get comprehensive emergency contact information"""
        
        contacts = [
            {
                "service": "Emergency Services", 
                "number": "911", 
                "description": "Life-threatening emergencies",
                "type": "emergency"
            },
            {
                "service": "Poison Control", 
                "number": "1-800-222-1222", 
                "description": "Poisoning emergencies",
                "type": "poison"
            },
            {
                "service": "Crisis Text Line", 
                "number": "Text HOME to 741741", 
                "description": "Mental health crisis support",
                "type": "mental_health"
            },
            {
                "service": "National Suicide Prevention Lifeline", 
                "number": "988", 
                "description": "Suicide prevention and mental health crisis",
                "type": "mental_health"
            }
        ]
        
        return contacts
    
    async def _get_rag_evidence(self, diagnosis: str) -> List[str]:
        """Get supporting medical evidence (placeholder for RAG system)"""
        
        # Placeholder for RAG system integration
        evidence = [
            f"Medical literature supports diagnosis of {diagnosis}",
            "Treatment guidelines recommend specialist consultation",
            "Evidence-based approach confirms diagnostic accuracy"
        ]
        
        return evidence
    
    async def _get_telemedicine_options(self, specialist_type: str) -> List[Dict[str, Any]]:
        """Get telemedicine options for the specialist type"""
        
        # Common telemedicine platforms (could be dynamically populated)
        telemedicine_options = [
            {
                "platform": "Teladoc",
                "specialties": ["general medicine", "dermatology", "mental health"],
                "availability": "24/7",
                "website": "teladoc.com"
            },
            {
                "platform": "MDLive",
                "specialties": ["family medicine", "urgent care", "therapy"],
                "availability": "24/7",
                "website": "mdlive.com"
            },
            {
                "platform": "Amwell",
                "specialties": ["primary care", "psychiatry", "nutrition"],
                "availability": "7am-11pm",
                "website": "amwell.com"
            }
        ]
        
        # Filter by relevance to specialist type
        relevant_options = []
        specialist_lower = specialist_type.lower()
        
        for option in telemedicine_options:
            if any(specialty in specialist_lower for specialty in option["specialties"]):
                relevant_options.append(option)
        
        # If no specific match, return general options
        return relevant_options if relevant_options else telemedicine_options
    
    async def _generate_cost_estimates(self, care_type: str, specialist_type: str) -> Dict[str, str]:
        """Generate cost estimates for different care types"""
        
        cost_estimates = {}
        
        if care_type == "emergency":
            cost_estimates = {
                "emergency_room_visit": "$1,500 - $3,000",
                "ambulance": "$400 - $1,200",
                "diagnostic_tests": "$200 - $1,000"
            }
        elif care_type == "specialist":
            cost_estimates = {
                "initial_consultation": "$200 - $500",
                "follow_up_visit": "$100 - $300",
                "diagnostic_tests": "$100 - $800"
            }
        else:  # self_care
            cost_estimates = {
                "over_counter_medications": "$10 - $50",
                "telemedicine_consultation": "$40 - $100",
                "home_monitoring_devices": "$20 - $200"
            }
        
        return cost_estimates
    
    def _calculate_distance(self, loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
        """Calculate distance between two coordinates in kilometers"""
        try:
            from math import radians, cos, sin, asin, sqrt
            
            lat1, lon1 = radians(loc1["lat"]), radians(loc1["lng"])
            lat2, lon2 = radians(loc2["lat"]), radians(loc2["lng"])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            km = 6371 * c
            
            return round(km, 1)
        except Exception:
            return 999.0
    
    def _get_search_radius_text(self, urgency: str) -> str:
        """Get human-readable search radius"""
        radius_km = self.urgency_radius.get(urgency, 25000) / 1000
        return f"{radius_km}km ({urgency} care radius)"
    
    def _get_default_recommendation(self) -> Dict[str, Any]:
        """Enhanced default recommendation"""
        return {
            "recommendation_type": "see_specialist",
            "specialist_type": "general practitioner",
            "appointment_urgency": "within_month",
            "self_care_advice": ["Consult with a healthcare professional for proper diagnosis"],
            "nearby_facilities": [],
            "facility_search_radius": "25km (default radius)",
            "emergency_contacts": [],
            "insurance_guidance": ["Contact your insurance provider for coverage information"],
            "rag_evidence": [],
            "telemedicine_options": [],
            "cost_estimates": {"consultation": "$100 - $300"}
        }