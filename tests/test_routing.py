from app.graphs.supervisor import route

def test_routes_quiz(): assert route({"query":"quiz me on attention"}) == "quiz"
def test_routes_research(): assert route({"query":"find a research gap in RAG"}) == "research"
def test_default_qa(): assert route({"query":"what is attention?"}) == "qa"
