"""
COMMIT 8: RAG Preparation CLI
Command-line interface pour préparer les embeddings
"""

import logging
from pathlib import Path
import click
from app.database import SessionLocal, engine
from app.rag.pipeline import RAGPreparationPipeline, FormationRAGIndexer
from app.rag.embeddings import MockEmbeddingModel, HuggingFaceEmbeddingModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default RAG data directory
RAG_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "rag"


@click.group()
def cli():
    """RAG preparation utilities"""
    pass


@cli.command()
@click.option('--strategy', default='semantic', help='Chunking strategy: semantic, paragraph, sentence, sliding_window')
@click.option('--chunk-size', default=512, help='Chunk size in tokens')
@click.option('--use-mock', is_flag=True, default=True, help='Use mock embeddings (faster for dev)')
@click.option('--max-formations', default=None, type=int, help='Limit to N formations (for testing)')
@click.option('--output-dir', default=str(RAG_DATA_DIR), help='Output directory for RAG data')
def prepare(strategy, chunk_size, use_mock, max_formations, output_dir):
    """Prepare RAG embeddings from database"""
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("="*70)
    logger.info("RAG PREPARATION PIPELINE")
    logger.info("="*70)
    logger.info(f"Strategy: {strategy}")
    logger.info(f"Chunk size: {chunk_size}")
    logger.info(f"Use mock embeddings: {use_mock}")
    logger.info(f"Max formations: {max_formations}")
    logger.info(f"Output directory: {output_dir}")
    logger.info("="*70)
    
    try:
        # Create pipeline
        pipeline = RAGPreparationPipeline(
            chunking_strategy=strategy,
            chunk_size=chunk_size,
            use_mock_embeddings=use_mock,
            cache_dir=output_dir
        )
        
        # Get database session
        db = SessionLocal()
        
        try:
            # Process formations
            embedding_store = pipeline.prepare_from_database(
                db,
                batch_size=50,
                max_formations=max_formations
            )
            
            # Display stats
            stats = pipeline.get_stats()
            logger.info("\n" + "="*70)
            logger.info("RAG PREPARATION COMPLETE")
            logger.info("="*70)
            logger.info(f"📊 Formations processed: {stats['formations_processed']}")
            logger.info(f"📄 Total chunks: {stats['total_chunks']}")
            logger.info(f"🔢 Embeddings generated: {stats['total_embeddings_generated']}")
            logger.info(f"⏱️  Processing time: {stats['processing_time_seconds']:.2f}s")
            if stats['errors']:
                logger.warning(f"⚠️  Errors: {len(stats['errors'])}")
            logger.info("="*70)
            
            # Save
            logger.info(f"\n💾 Saving RAG data to {output_dir}...")
            pipeline.save(output_dir)
            logger.info("✅ RAG data saved successfully!")
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


@cli.command()
@click.option('--rag-dir', default=str(RAG_DATA_DIR), help='RAG data directory')
@click.option('--top-k', default=5, type=int, help='Number of results to return')
@click.argument('query')
def search(rag_dir, top_k, query):
    """Search for formations using RAG"""
    
    rag_dir = Path(rag_dir)
    
    if not rag_dir.exists():
        click.echo(f"Error: RAG data directory not found: {rag_dir}")
        click.echo("Run 'python -m app.cli.rag_cli prepare' first")
        return
    
    logger.info("="*70)
    logger.info(f"SEARCHING: '{query}'")
    logger.info("="*70)
    
    try:
        # Load RAG data
        pipeline = RAGPreparationPipeline(use_mock_embeddings=True)
        embedding_store = pipeline.load(rag_dir)
        
        # Create indexer
        indexer = FormationRAGIndexer(embedding_store)
        
        # Search
        results = indexer.search(query, pipeline.embedding_model, top_k=top_k)
        
        # Display results
        click.echo(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            click.echo(f"{i}. {result['intitule']}")
            click.echo(f"   Formation: {result['formation_id']}")
            click.echo(f"   Établissement: {result['etablissement']}")
            click.echo(f"   Ville: {result['metadata'].get('ville', 'N/A')}")
            click.echo(f"   Domaine: {result['domaine']}")
            click.echo(f"   Score: {result['similarity_score']:.4f}")
            click.echo(f"   Keywords: {', '.join(result['keywords'])}")
            click.echo()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


@cli.command()
@click.option('--rag-dir', default=str(RAG_DATA_DIR), help='RAG data directory')
def info(rag_dir):
    """Show RAG data information"""
    
    rag_dir = Path(rag_dir)
    stats_file = rag_dir / "stats.json"
    
    if not stats_file.exists():
        click.echo(f"Error: stats.json not found in {rag_dir}")
        return
    
    import json
    with open(stats_file, 'r') as f:
        stats = json.load(f)
    
    click.echo("\n" + "="*70)
    click.echo("RAG DATA INFORMATION")
    click.echo("="*70)
    click.echo(f"Formations processed: {stats['formations_processed']}")
    click.echo(f"Total chunks: {stats['total_chunks']}")
    click.echo(f"Embeddings generated: {stats['total_embeddings_generated']}")
    click.echo(f"Processing time: {stats['processing_time_seconds']:.2f}s")
    click.echo(f"Errors: {len(stats['errors'])}")
    click.echo("="*70 + "\n")


if __name__ == '__main__':
    cli()
