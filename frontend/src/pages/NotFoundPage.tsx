import { PixelButton } from '@/components/PixelButton';

export function NotFoundPage() {
  return (
    <div className="min-h-[50dvh] flex flex-col items-center justify-center px-4">
      <h1 className="font-pixel text-sm text-cream-200">NO ROUTE</h1>
      <p className="mt-2 text-sm text-cream-200/60 font-body text-center max-w-sm">
        The path is not part of this client. Return to the home or hub.
      </p>
      <div className="mt-4 flex flex-wrap justify-center gap-2">
        <PixelButton to="/" variant="solid">HOME</PixelButton>
        <PixelButton to="/hub" variant="ghost">HUB</PixelButton>
      </div>
    </div>
  );
}
