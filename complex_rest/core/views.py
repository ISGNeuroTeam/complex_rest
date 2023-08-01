from rest_framework.response import Response
from drf_spectacular.views import SpectacularAPIView


class SpectacularAPIView(SpectacularAPIView):
    def _get_schema_response(self, request):
        # version specified as parameter to the view always takes precedence. after
        # that we try to source version through the schema view's own versioning_class.
        version = self.api_version or request.version or self._get_version_parameter(request)
        generator = self.generator_class(urlconf=self.urlconf, api_version=version, patterns=self.patterns)
        data = generator.get_schema(request=request, public=self.serve_public)
        data['paths'] = {key.replace('//', '/'): value for key, value in data['paths'].items()}
        return Response(
            data=data,
            headers={"Content-Disposition": f'inline; filename="{self._get_filename(request, version)}"'}
        )

