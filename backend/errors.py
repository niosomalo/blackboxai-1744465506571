from flask import jsonify

class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

def init_error_handlers(app):
    """Initialize error handlers for the Flask app"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Bad request'
        }), 400

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

class ResourceNotFoundError(APIError):
    """Raised when a requested resource is not found"""
    def __init__(self, message='Resource not found'):
        super().__init__(message=message, status_code=404)

class ValidationError(APIError):
    """Raised when input validation fails"""
    def __init__(self, message='Validation error'):
        super().__init__(message=message, status_code=400)

class StockError(APIError):
    """Raised when there's insufficient stock"""
    def __init__(self, message='Insufficient stock'):
        super().__init__(message=message, status_code=400)
