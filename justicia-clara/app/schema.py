"""Pydantic models for Spanish legal document structure."""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class EncabezadoInstitucional(BaseModel):
    """Institutional header of the legal document."""
    
    roj: Optional[str] = Field(None, description="ROJ identifier")
    ecli: Optional[str] = Field(None, description="ECLI (European Case Law Identifier)")
    id_cendoj: Optional[str] = Field(None, description="Cendoj ID")
    organo_judicial: Optional[str] = Field(None, description="Judicial body (e.g., Juzgado de Primera Instancia nº __)")
    sede_seccion: Optional[str] = Field(None, description="Court location and section")
    fecha_resolucion: Optional[date] = Field(None, description="Resolution date")
    numero_recurso: Optional[str] = Field(None, description="Appeal number")
    numero_resolucion: Optional[str] = Field(None, description="Resolution number")
    tipo_procedimiento: Optional[str] = Field(None, description="Procedure type (ordinario, verbal, etc.)")
    nombre_ponente_juez: Optional[str] = Field(None, description="Name of the judge or rapporteur")
    tipo_resolucion: Optional[str] = Field(None, description="Resolution type (Sentencia / Auto)")


class IdentificacionPartes(BaseModel):
    """Party identification section."""
    
    nombre_demandante: Optional[str] = Field(None, description="Plaintiff name")
    nombre_demandado: Optional[str] = Field(None, description="Defendant name")
    nombre_procuradores: Optional[List[str]] = Field(default_factory=list, description="Names of court representatives (procuradores)")
    nombre_abogados: Optional[List[str]] = Field(default_factory=list, description="Names of lawyers (if present)")
    representacion_apoderamiento: Optional[str] = Field(None, description="Representation and power of attorney details")


class AntecedentesHecho(BaseModel):
    """Factual background section."""
    
    descripcion_proceso: Optional[str] = Field(None, description="Process description (demanda, contestación, audiencia previa)")
    relato_hechos_relevantes: Optional[str] = Field(None, description="Narrative of relevant or proven facts")
    mencion_pruebas_practicadas: Optional[str] = Field(None, description="Mention of evidence presented")
    cumplimiento_prescripciones_legales: Optional[str] = Field(None, description="Compliance with legal processing requirements")


class FundamentosDerecho(BaseModel):
    """Legal grounds section."""
    
    exposicion_juridica: Optional[str] = Field(None, description="Structured legal exposition (PRIMERO, SEGUNDO, etc.)")
    normas_aplicables: Optional[List[str]] = Field(default_factory=list, description="Applicable laws (Código Civil, LEC, Ley de Usura, etc.)")
    citas_jurisprudencia: Optional[List[str]] = Field(default_factory=list, description="Case law citations (Tribunal Supremo, Audiencias Provinciales, TJUE)")
    aplicacion_derecho_caso: Optional[str] = Field(None, description="Application of law to the specific case")
    razonamiento_logico: Optional[str] = Field(None, description="Logical reasoning leading to the ruling")


class DecisionFallo(BaseModel):
    """Decision/ruling section."""
    
    epigrafe: Optional[str] = Field(None, description="'FALLO' heading or equivalent")
    declaracion_expresa: Optional[str] = Field(None, description="Explicit declaration of what is granted or denied")
    consecuencias_juridicas: Optional[str] = Field(None, description="Legal consequences (nulidad, condena, restitución, etc.)")
    ejecucion_determinacion_posterior: Optional[str] = Field(None, description="Execution or subsequent determination (if applicable)")


class CostasProcesales(BaseModel):
    """Legal costs section."""
    
    pronunciamiento_costas: Optional[str] = Field(None, description="Ruling on costs (who pays and why)")


class Recursos(BaseModel):
    """Appeals section."""
    
    es_firme: Optional[bool] = Field(None, description="Whether the judgment is final (firme) or appealable")
    plazo_recurso: Optional[str] = Field(None, description="Appeal deadline")
    organo_competente_recurso: Optional[str] = Field(None, description="Competent body for appeal (typically Audiencia Provincial)")


class ClausulaProteccionDatos(BaseModel):
    """Data protection clause."""
    
    advertencia_tratamiento_datos: Optional[str] = Field(None, description="Warning about personal data treatment or anonymization")
    limitaciones_difusion: Optional[str] = Field(None, description="Limitations on judgment dissemination")


class DocumentoLegal(BaseModel):
    """Complete legal document structure."""
    
    encabezado_institucional: Optional[EncabezadoInstitucional] = Field(None, description="Institutional header")
    identificacion_partes: Optional[IdentificacionPartes] = Field(None, description="Party identification")
    antecedentes_hecho: Optional[AntecedentesHecho] = Field(None, description="Factual background")
    fundamentos_derecho: Optional[FundamentosDerecho] = Field(None, description="Legal grounds")
    decision_fallo: Optional[DecisionFallo] = Field(None, description="Decision/ruling")
    costas_procesales: Optional[CostasProcesales] = Field(None, description="Legal costs")
    recursos: Optional[Recursos] = Field(None, description="Appeals information")
    clausula_proteccion_datos: Optional[ClausulaProteccionDatos] = Field(None, description="Data protection clause")


# Legacy model for backward compatibility (if needed)
class SimplifyResult(BaseModel):
    """Result of text simplification process."""
    
    original: str = Field(..., description="Original text")
    simplified: str = Field(..., description="Simplified text")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Semantic similarity score")
    checks: dict = Field(default_factory=dict, description="Deterministic validation checks")
    judge: Optional[dict] = Field(None, description="LLM judge evaluation")

