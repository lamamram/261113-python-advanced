class ArticleNonTrouveException(Exception):
    def __init__(self, article_id: int):
        self.article_id = article_id