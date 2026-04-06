import {AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig, spring, interpolate} from 'remotion';

export const HelloWorld = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const titleOpacity = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    durationInFrames: 30,
  });

  const problemSlide = interpolate(frame, [60, 90], [100, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const solutionSlide = interpolate(frame, [150, 180], [100, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill className="bg-slate-900">
      <Sequence from={0} durationInFrames={60}>
        <AbsoluteFill 
          className="flex flex-col items-center justify-center"
          style={{opacity: titleOpacity}}
        >
          <h1 className="text-8xl font-bold text-white text-center mb-5">
            Agente de Reportes AI
          </h1>
          <p className="text-4xl text-slate-400">
            Automatización para Consultoras
          </p>
        </AbsoluteFill>
      </Sequence>

      <Sequence from={60} durationInFrames={90}>
        <AbsoluteFill 
          className="flex items-center justify-center"
          style={{transform: `translateX(${problemSlide}%)`}}
        >
          <div className="bg-slate-800 p-16 rounded-3xl max-w-4xl">
            <h2 className="text-6xl text-red-500 mb-10">❌ El Problema</h2>
            <p className="text-4xl text-white leading-relaxed">
              Las consultoras pierden <strong>8 horas semanales</strong> armando reportes manualmente
            </p>
            <div className="text-3xl text-slate-400 mt-8 space-y-2">
              <p>• Copiar datos de múltiples fuentes</p>
              <p>• Calcular métricas manualmente</p>
              <p>• Formatear documentos</p>
            </div>
          </div>
        </AbsoluteFill>
      </Sequence>

      <Sequence from={150} durationInFrames={90}>
        <AbsoluteFill 
          className="flex items-center justify-center"
          style={{transform: `translateX(${solutionSlide}%)`}}
        >
          <div className="bg-slate-800 p-16 rounded-3xl max-w-4xl">
            <h2 className="text-6xl text-green-500 mb-10">✅ La Solución</h2>
            <p className="text-4xl text-white leading-relaxed">
              Agente automatizado genera reportes completos en <strong>segundos</strong>
            </p>
          </div>
        </AbsoluteFill>
      </Sequence>

      <Sequence from={240} durationInFrames={120}>
        <AbsoluteFill className="flex flex-col items-center justify-center p-16">
          <h2 className="text-6xl text-green-500 mb-16 text-center">
            📊 Resultados Automáticos
          </h2>
          <div className="grid grid-cols-2 gap-10 max-w-5xl">
            <div className="bg-slate-800 p-10 rounded-2xl">
              <div className="text-5xl mb-5">🕐</div>
              <div className="text-3xl text-white">91.0 horas rastreadas</div>
            </div>
            <div className="bg-slate-800 p-10 rounded-2xl">
              <div className="text-5xl mb-5">💰</div>
              <div className="text-3xl text-white">$13,496.95 facturados</div>
            </div>
            <div className="bg-slate-800 p-10 rounded-2xl">
              <div className="text-5xl mb-5">💵</div>
              <div className="text-3xl text-white">$21,750 en ingresos</div>
            </div>
            <div className="bg-slate-800 p-10 rounded-2xl">
              <div className="text-5xl mb-5">📋</div>
              <div className="text-3xl text-white">4 tareas priorizadas</div>
            </div>
          </div>
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};