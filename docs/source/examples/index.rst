:github_url: https://github.com/merlinquantum/merlin

.. raw:: html

    <style>
        .examples-container {
            width: 100%;
            margin: 0 auto;
        }
        
        .section-header {
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #0ec8c3;
        }
        
        .section-header h2 {
            color: #333;
            font-size: 24px;
            margin: 0;
            font-weight: 600;
        }
        
        .section-description {
            color: #666;
            font-size: 14px;
            margin: 10px 0 20px 0;
        }
        
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .gallery-card {
            text-align: center;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none !important;
            color: inherit !important;
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        
        .gallery-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .gallery-card img {
            width: 100%;
            height: 150px;
            object-fit: cover;
            display: block;
        }
        
        .gallery-card-title {
            padding: 12px 10px;
            font-size: 13px;
            font-weight: 500;
            color: #333;
            line-height: 1.4;
            flex-grow: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            border-top: 1px solid #f0f0f0;
        }
        
        .gallery-card:hover .gallery-card-title {
            color: #0ec8c3;
        }
    </style>

Examples
========

Explore MerLin examples across different categories below. Browse notebooks, reproduced papers, and backend implementations to get started with quantum machine learning.

.. raw:: html

    <div class="examples-container">
    
        <div class="section-header">
            <h2>📓 Jupyter Notebooks</h2>
        </div>
        <div class="section-description">
            Step-by-step tutorials and demonstrations of MerLin features
        </div>
        <div class="gallery-grid">
            <a href="auto_examples/notebooks/plot_iris_onboarding.html" class="gallery-card">
                <img src="../_static/examples/iris_sepal_classes.png" alt="First Quantum Layers">
                <div class="gallery-card-title">First Quantum Layers (Iris)</div>
            </a>
        </div>
    
        <div class="section-header">
            <h2>📄 Reproduced Papers</h2>
        </div>
        <div class="section-description">
            Quantum machine learning papers reproduced with MerLin
        </div>
        <div class="gallery-grid">
            <a href="auto_examples/reproduced_papers/plot_reproduced_papers.html" class="gallery-card">
                <img src="../_static/examples/iris.svg" alt="Reproduced Papers">
                <div class="gallery-card-title">QML Paper Reproductions</div>
            </a>
        </div>
    
        <div class="section-header">
            <h2>⚙️ Rust Backend</h2>
        </div>
        <div class="section-description">
            Explore the Rust backend implementation and GPU-optimized simulator
        </div>
        <div class="gallery-grid">
            <a href="auto_examples/rust/plot_rust_backend_walkthrough.html" class="gallery-card">
                <img src="../_static/examples/rust.svg" alt="Rust Backend">
                <div class="gallery-card-title">Rust Simulator Backend</div>
            </a>
        </div>
    
    </div>
