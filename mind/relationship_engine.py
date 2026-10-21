import os
import json
from typing import List, Dict, Tuple
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class Entity(BaseModel):
    id: str = Field(description="Unique identifier for the entity (lowercase, underscored)")
    label: str = Field(description="Human-readable name of the entity")
    type: str = Field(description="Category of the entity (e.g., Person, Concept, Organization, Event)")

class Relationship(BaseModel):
    source: str = Field(description="ID of the source entity")
    target: str = Field(description="ID of the target entity")
    relation: str = Field(description="The nature of the relationship (e.g., 'is_a', 'part_of', 'influences', 'contradicts')")

class GraphData(BaseModel):
    nodes: List[Entity]
    edges: List[Relationship]

class RelationshipExtractionEngine:
    def __init__(self, api_key: str, storage_path: str = "/root/lumina_mind_prod/graph_store.json"):
        self.api_key = api_key
        self.storage_path = storage_path
        os.environ["OPENAI_API_KEY"] = api_key
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.parser = JsonOutputParser(pydantic_object=GraphData)
        
        # Initialize storage if not exists
        if not os.path.exists(self.storage_path):
            self._save_graph({"nodes": [], "edges": []})

    def _save_graph(self, data: Dict):
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_graph(self) -> Dict:
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"nodes": [], "edges": []}

    def extract_and_store(self, text: str):
        """
        Extracts entities and relationships from text and merges them into the graph store.
        """
        prompt = PromptTemplate(
            template="""You are a Knowledge Graph Extractor. Analyze the following text and extract key entities and their relationships.
            
            Text:
            {text}
            
            Instructions:
            1. Identify all significant entities (concepts, people, organizations, etc.).
            2. Identify the relationships between these entities.
            3. Ensure entity IDs are consistent and lowercase.
            4. Return the output strictly as JSON matching the requested schema.
            
            {format_instructions}
            """,
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

        chain = prompt | self.llm | self.parser
        extracted = chain.invoke({"text": text})
        
        # Merge with existing graph
        current_graph = self._load_graph()
        
        # Deduplicate and add nodes
        existing_node_ids = {node["id"] for node in current_graph["nodes"]}
        for node in extracted.get("nodes", []):
            if node["id"] not in existing_node_ids:
                current_graph["nodes"].append(node)
                existing_node_ids.add(node["id"])
        
        # Deduplicate and add edges
        existing_edges = { (edge["source"], edge["target"], edge["relation"]) for edge in current_graph["edges"] }
        for edge in extracted.get("edges", []):
            edge_tuple = (edge["source"], edge["target"], edge["relation"])
            if edge_tuple not in existing_edges:
                current_graph["edges"].append(edge)
                existing_edges.add(edge_tuple)
        
        self._save_graph(current_graph)
        return extracted

    def get_graph(self) -> Dict:
        """Returns the full current knowledge graph."""
        return self._load_graph()
