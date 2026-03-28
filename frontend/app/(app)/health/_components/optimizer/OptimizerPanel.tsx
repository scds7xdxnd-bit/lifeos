'use client'

import { useState, useMemo, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { foodLibraryApi } from '@/lib/api/foodLibrary'
import { calculatorApi } from '@/lib/api/calculator'
import type { HealthPageTranslations } from '@/lib/translations/app'
import { useLang } from '@/lib/useLang'
import {
  solveLP,
  type ObjectiveMode,
  type Constraint,
  type FoodBounds,
  type SolveOutput,
} from '@/lib/optimizer/solveLP'
import { FoodLibraryManager } from './FoodLibraryManager'
import { FoodItemForm } from './FoodItemForm'
import { ObjectiveSelector } from './ObjectiveSelector'
import { ConstraintBuilder } from './ConstraintBuilder'
import { FoodBoundsEditor } from './FoodBoundsEditor'
import { OptimizerResult } from './OptimizerResult'

interface Props {
  t: HealthPageTranslations
  onSwitchToCalculator?: () => void
}

const CARD: React.CSSProperties = {
  background: '#ffffff',
  borderRadius: '0 16px 16px 16px',
  padding: 24,
}

const MICRO: React.CSSProperties = {
  fontFamily: 'Manrope, sans-serif',
  fontSize: '0.6875rem',
  fontWeight: 700,
  letterSpacing: '0.05em',
  textTransform: 'uppercase' as const,
}

export function OptimizerPanel({ t, onSwitchToCalculator }: Props) {
  const [lang] = useLang()

  // Food library UI state

  const [showFoodForm, setShowFoodForm] = useState(false)
  const [foodFormMode, setFoodFormMode] = useState<'create' | 'edit'>('create')
  const [editingFoodId, setEditingFoodId] = useState<number | null>(null)

  // Optimizer inputs
  const [selectedFoodIds, setSelectedFoodIds] = useState<Set<number>>(new Set())
  const [objective, setObjective] = useState<ObjectiveMode | null>(null)
  const [targetValue, setTargetValue] = useState(0)
  const [constraints, setConstraints] = useState<Constraint[]>([])
  const [foodBounds, setFoodBounds] = useState<FoodBounds>({})
  const [horizonDays, setHorizonDays] = useState<number>(30)

  // Live result — updated automatically
  const [result, setResult] = useState<SolveOutput | null>(null)

  const { data: foodData, isLoading } = useQuery({
    queryKey: ['health', 'food-library'],
    queryFn: () => foodLibraryApi.list(1, 200),
  })

  const { data: latestReport } = useQuery({
    queryKey: ['health', 'calculator', 'latest'],
    queryFn: () => calculatorApi.getLatestReport(),
  })

  // Auto-populate constraints from calculator report (only when empty)
  useEffect(() => {
    if (!latestReport?.report) return
    if (constraints.length > 0) return
    const r = latestReport.report
    const h = horizonDays
    setConstraints([
      { id: crypto.randomUUID(), category: 'calories', operator: '<=', value: Math.round(r.daily_calories * h), source: 'calculator' },
      { id: crypto.randomUUID(), category: 'protein', operator: '>=', value: Math.round(r.protein_g_per_day * h), source: 'calculator' },
      { id: crypto.randomUUID(), category: 'fat', operator: '>=', value: Math.round(r.fat_g_per_day * h), source: 'calculator' },
      { id: crypto.randomUUID(), category: 'carbohydrate', operator: '>=', value: Math.round(r.carbs_g_per_day * h), source: 'calculator' },
      { id: crypto.randomUUID(), category: 'fiber', operator: '>=', value: Math.round(r.fiber_g_per_day * h), source: 'calculator' },
    ])
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [latestReport])

  // Rescale calculator constraints when horizon changes
  useEffect(() => {
    if (!latestReport?.report) return
    const r = latestReport.report
    const h = horizonDays
    const dailyMap: Record<string, number> = {
      calories: r.daily_calories,
      protein: r.protein_g_per_day,
      fat: r.fat_g_per_day,
      carbohydrate: r.carbs_g_per_day,
      fiber: r.fiber_g_per_day,
    }
    setConstraints(prev => prev.map(c => {
      if (c.source !== 'calculator') return c
      const daily = dailyMap[c.category]
      if (daily == null) return c
      return { ...c, value: Math.round(daily * h) }
    }))
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [horizonDays])

  const allFoods = useMemo(() => foodData?.items ?? [], [foodData])
  const selectedFoods = useMemo(
    () => allFoods.filter(f => selectedFoodIds.has(f.id)),
    [allFoods, selectedFoodIds]
  )
  const editingFood = useMemo(
    () => allFoods.find(f => f.id === editingFoodId) ?? null,
    [allFoods, editingFoodId]
  )

  // Auto-solve: re-runs whenever any input changes
  useEffect(() => {
    if (selectedFoods.length === 0 || !objective) {
      setResult(null)
      return
    }
    setResult(solveLP({ foods: selectedFoods, objective, targetValue, constraints, bounds: foodBounds }))
  }, [selectedFoods, objective, targetValue, constraints, foodBounds])

  function toggleFood(id: number) {
    setSelectedFoodIds(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const openAddForm = () => { setFoodFormMode('create'); setEditingFoodId(null); setShowFoodForm(true) }
  const openEditForm = (id: number) => { setFoodFormMode('edit'); setEditingFoodId(id); setShowFoodForm(true) }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

      {/* ── Header ──────────────────────────────────────────────── */}
      <div>
        <p style={{ ...MICRO, color: '#8b4a3a', marginBottom: 4 }}>{t.macroCostOptimizer}</p>
        <h2 style={{ fontFamily: 'Newsreader, Georgia, serif', fontSize: '1.5rem', fontWeight: 300, color: '#2e342b', marginBottom: 6 }}>
          {t.planNutrition}
        </h2>
        <p style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.875rem', color: '#5a6157' }}>
          {t.planNutritionSub}
        </p>

        {/* Time horizon */}
        <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <span style={{ ...MICRO, color: '#8b4a3a' }}>{t.timeHorizon}</span>
          <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.875rem', color: '#5a6157' }}>{t.optimizingFor}</span>
          <select
            value={horizonDays}
            onChange={e => setHorizonDays(Number(e.target.value))}
            style={{ background: '#ffffff', border: '1px solid rgba(173,180,168,0.2)', borderRadius: 4, width: 60, padding: '4px 6px', fontFamily: 'Manrope, sans-serif', fontSize: '0.875rem', color: '#2e342b' }}
          >
            {[{ days: 30, months: 1 }, { days: 60, months: 2 }, { days: 90, months: 3 }, { days: 180, months: 6 }].map(({ days, months }) => (
              <option key={days} value={days}>{months}</option>
            ))}
          </select>
          <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.875rem', color: '#5a6157' }}>{t.months}</span>
        </div>
      </div>

      {/* ── Food item form (modal) ───────────────────────────────── */}
      {showFoodForm && (
        <FoodItemForm
          mode={foodFormMode}
          initialData={foodFormMode === 'edit' ? editingFood : null}
          t={t}
          lang={lang}
          onClose={() => setShowFoodForm(false)}
          onSuccess={() => setShowFoodForm(false)}
        />
      )}

      {/* ── No foods yet: full-width library ────────────────────── */}
      {allFoods.length === 0 && (
        <FoodLibraryManager
          t={t}
          foods={allFoods}
          isLoading={isLoading}
          onAddFood={openAddForm}
          onEditFood={openEditForm}
          selectedIds={selectedFoodIds}
          onToggle={toggleFood}
          onSelectAll={() => setSelectedFoodIds(new Set(allFoods.map(f => f.id)))}
          onDeselectAll={() => setSelectedFoodIds(new Set())}
        />
      )}

      {/* ── Main two-column layout ───────────────────────────────── */}
      {allFoods.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 3fr)',
          gap: 24,
          alignItems: 'start',
        }}>

          {/* ── LEFT: inputs ──────────────────────────────────────── */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

            {/* Food Library + Selection (combined) */}
            <FoodLibraryManager
              t={t}
              foods={allFoods}
              isLoading={isLoading}
              onAddFood={openAddForm}
              onEditFood={openEditForm}
              selectedIds={selectedFoodIds}
              onToggle={toggleFood}
              onSelectAll={() => setSelectedFoodIds(new Set(allFoods.map(f => f.id)))}
              onDeselectAll={() => setSelectedFoodIds(new Set())}
            />

            {/* Constraints */}
            <div style={CARD}>
              <ConstraintBuilder
                t={t}
                constraints={constraints}
                onChange={setConstraints}
                objectiveMode={objective}
                latestReportExists={!!latestReport?.report}
                onSwitchToCalculator={onSwitchToCalculator}
              />
            </div>

            {/* Food Bounds */}
            {selectedFoods.length > 0 && (
              <div style={CARD}>
                <FoodBoundsEditor
                  t={t}
                  selectedFoods={selectedFoods}
                  bounds={foodBounds}
                  onChange={setFoodBounds}
                />
              </div>
            )}
          </div>

          {/* ── RIGHT: objective + live result ────────────────────── */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16, position: 'sticky', top: 24 }}>

            {/* Objective Selector */}
            <div style={CARD}>
              <ObjectiveSelector
                t={t}
                value={objective}
                targetValue={targetValue}
                onChange={setObjective}
                onTargetChange={setTargetValue}
              />
            </div>

            {/* Empty state: no objective */}
            {!objective && (
              <div style={{ ...CARD, padding: '40px 32px', textAlign: 'center' }}>
                <div style={{ width: 40, height: 40, borderRadius: '50%', background: '#f1f5eb', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8b4a3a" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                  </svg>
                </div>
                <p style={{ ...MICRO, color: '#adb4a8', marginBottom: 10 }}>{t.awaitingObjective}</p>
                <p style={{ fontFamily: 'Newsreader, Georgia, serif', fontSize: '1.125rem', fontWeight: 300, color: '#2e342b', marginBottom: 8, lineHeight: 1.4 }}>
                  {t.chooseAnObjective}
                </p>
                <p style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#767d72', lineHeight: 1.6 }}>
                  {t.chooseAnObjectiveSub}
                </p>
              </div>
            )}

            {/* Empty state: objective set but no foods */}
            {objective && selectedFoods.length === 0 && (
              <div style={{ ...CARD, padding: '40px 32px', textAlign: 'center' }}>
                <div style={{ width: 40, height: 40, borderRadius: '50%', background: '#f1f5eb', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4b6646" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
                  </svg>
                </div>
                <p style={{ ...MICRO, color: '#adb4a8', marginBottom: 10 }}>{t.noFoodsSelected}</p>
                <p style={{ fontFamily: 'Newsreader, Georgia, serif', fontSize: '1.125rem', fontWeight: 300, color: '#2e342b', marginBottom: 8, lineHeight: 1.4 }}>
                  {t.selectYourFoods}
                </p>
                <p style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#767d72', lineHeight: 1.6 }}>
                  {t.selectYourFoodsSub}
                </p>
              </div>
            )}

            {/* Live result */}
            {objective && selectedFoods.length > 0 && result !== null && (
              <OptimizerResult
                t={t}
                result={result}
                error={null}
                objectiveMode={objective}
                onAdjustConstraints={undefined}
              />
            )}
          </div>

        </div>
      )}
    </div>
  )
}
