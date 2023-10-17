from collections import Counter
from dataclasses import dataclass
import streamlit as st
# from streamlit_elements import elements, dashboard, mui, editor, media, lazy, sync, nivo
from omnibelt import load_yaml, save_yaml
from . import misc
from .general import Quantity, PctChange, country_flags, sector_emojis, sector_colors


_dis_root = misc.assets_root() / 'dis'


class World:
	cfg = None
	def __init__(self, infos, features):
		self.infos = infos
		self.features = features

	def __iter__(self):
		return iter(self.infos)

	default_features = [
		'price',
		'yield',
		'peg_ratio',
		'shares',
		'beta',
		'log_market_cap',
		'recommendation_mean',
		'overall_risk',
		'ibsym',
		'sector',
		'country',
		'industry',
	]

	@classmethod
	def load_ticker(cls, yfsym: str):
		container_source = cls.cfg.peek('container')
		with container_source.silence():
			date = cls.cfg.pull('date', 'last')
			date = str(date)
			ctx = container_source.create()
		ctx['ticker'] = yfsym
		ctx['date'] = date
		return ctx

	@classmethod
	def create(cls, path=None, name=None):
		if path is None:
			if name is None:
				name = cls.cfg.pull('portfolio', None)
			if name is not None:
				path = _dis_root / f'{name}.yaml'

		features = cls.cfg.pull('features', cls.default_features)

		if path is None:
			tickers = cls.cfg.pull('tickers', [], silent=True)
			cls.cfg.print(f'Found {len(tickers)} tickers.')
			if isinstance(tickers, list):
				tickers = {tk: {} for tk in tickers}
		else:
			if not path.exists():
				raise FileNotFoundError(f'Portfolio {name} not found.')
			raw = load_yaml(path) if path.exists() else {}
			tickers = raw.get('tickers', {})
			print(f'Loaded portfolio {name} with {len(tickers)} symbols.')
			tickers = {item['ticker']: item for item in tickers}
			print(f'Found {len(tickers)} symbols in the current universe.')
			if 'features' in raw:
				features = raw['features']

		total = sum(e.get('weight', 0.) for e in tickers.values())
		for k, v in tickers.items():
			v['weight'] = 100. * (v.get('weight', 0.) / total if total > 0 else 1 / len(tickers))

		infos = [cls.load_ticker(yfsym) for yfsym in tickers]

		for i, info in enumerate(infos):
			loaded = tickers.get(info['ticker'], {})
			info['order'] = loaded.get('order', i)
			info['sel'] = loaded.get('sel', False)
			info['weight'] = loaded.get('weight', 0.)
			info['hidden'] = loaded.get('hidden', False)
		# infos = infos[:5]
		cols = ['sel', 'weight', 'ticker', *features]
		for info in infos:
			for col in cols:
				val = info[col]
				if isinstance(val, (Quantity, PctChange)):
					info[col] = val.amount

			info['locked'] = False

		return cls(infos, features=features)

	def export(self, path, include_hidden=False, include_sector=True, include_country=True):

		tickers = [{k: v for k, v in info.items() if k in ['ticker', 'weight', 'sel', 'hidden', 'order']}
				   for info in self.infos]
		tickers.sort(key=lambda info: info['weight'], reverse=True)

		raw = {
			'tickers': tickers,
		}
		# if include_sector:
		# 	sectors = []
		#
		#
		# 	raw['sectors'] =

		save_yaml(raw, path)



class Formatter:
	def set_world(self, world):
		pass

	def column_config(self, key):
		pass

	def format_key(self, key):
		return key

	def format_value(self, key, value):
		return value


class DisplayData:
	def __init__(self, world,):
		self.max_weight = 100.
		self.cards = None
		self.sectors = None
		self.countries = None
		self.stats = None
		self.world = world
		self.populate(world.infos, world.features)

	def populate(self, infos, features):
		cards = [Card(info, features) for info in infos]
		self.max_weight = max(10., min(float(int(420 / len(cards))//10*10), 100.))
		self.delta = self.max_weight / 50
		for c in cards:
			# c.weight = 100/len(cards)
			c.max_weight = self.max_weight
			c.set_portfolio(self)
		self.cards = cards
		self.sectors = [k for k, v  in Counter(c.sector for c in cards).most_common()]
		self.countries = [k for k, v  in Counter(c.country for c in cards).most_common()]
		self.stats = list(features)

	def update_weights(self, deltas: dict['Card', float]):
		# print(f'Updating weights by {deltas}')
		locked = [c for c in deltas if c.locked]
		assert len(locked) == 0, f'Cannot update weight of {len(locked)} locked cards: {locked}'

		other = [c for c in self.cards if c not in deltas and not c.locked]

		if not len(other):
			st.error(f'Cannot update weights, there are no others')
			return

		fixed = {card: max(-card.weight, min(delta, self.max_weight - card.weight))
					for card, delta in deltas.items()}
		total = sum(fixed.values())
		avail = sum(c.weight for c in other)

		if total > 0:
			if total > avail:
				fixed.update({card: prev * avail / total for card, prev in fixed.items() if prev > 0})
				fixed.update({card: -card.weight for card in other})
			else:
				fixed.update({card: -total * card.weight / avail for card in other})

		elif total < 0:
			cap = sum(self.max_weight - c.weight for c in other)
			if -total > cap:
				fixed.update({card: prev * cap / -total for card, prev in fixed.items() if prev < 0})
				fixed.update({card: self.max_weight - card.weight for card in other})
			else:
				fixed.update({card: -total * (self.max_weight - card.weight) / cap for card in other})

		assert abs(sum(fixed.values())) < 0.001, f'{fixed}'

		for card, delta in fixed.items():
			card.weight += delta

		assert abs(100 - sum(c.weight for c in self.cards)) < 0.001, f'{sum(c.weight for c in self.cards)}'

	def _select_all(self):
		num_sel, num_new = 0, 0
		for c in self.cards:
			if not c.hidden:
				num_sel += 1
				if not c.selected:
					num_new += 1
				c.selected = True
		st.toast(f'Selected {num_sel} stocks ({num_new} new)')

	def _deselect_all(self):
		num_sel, num_new = 0, 0
		for c in self.cards:
			if not c.hidden:
				num_sel += 1
				if c.selected:
					num_new += 1
				c.selected = False
		st.toast(f'Deselected {num_sel} stocks ({num_new} new)')

	def _invert_selection(self):
		num_sel = 0
		for c in self.cards:
			if not c.hidden:
				c.selected = not c.selected
				if c.selected:
					num_sel += 1
		st.toast(f'Inverted selection ({num_sel} selected)')

	def _show_all(self):
		num_new = 0
		for c in self.cards:
			if c.hidden:
				num_new += 1
			c.hidden = False
			c.selected = False
		st.toast(f'Showing all ({num_new} were hidden)')

	def _hide_selected(self):
		num_hidden = 0
		for c in self.cards:
			if c.selected:
				num_hidden += 1
				c.hidden = True
				c.selected = False
		st.toast(f'{num_hidden} stocks hidden')

	def _lock_hidden(self):
		num_locked, num_new = 0, 0
		for c in self.cards:
			if c.hidden:
				num_locked += 1
				if not c.locked:
					num_new += 1
				c.locked = True
		st.toast(f'Locked {num_locked} stocks ({num_new} new)')

	def _lock_selected(self):
		num_locked, num_new = 0, 0
		for c in self.cards:
			if not c.hidden and c.selected:
				num_locked += 1
				if not c.locked:
					num_new += 1
				c.locked = True
		st.toast(f'Locked {num_locked} stocks ({num_new} new)')

	def _unlock_selected(self):
		num_locked, num_new = 0, 0
		for c in self.cards:
			if not c.hidden and c.selected:
				num_locked += 1
				if c.locked:
					num_new += 1
				c.locked = False
		st.toast(f'Unlocked {num_locked} stocks ({num_new} new)')

	def _apply_selection(self, select_sectors, select_country, select_stat, side, threshold):

		sectors = [s for s in select_sectors if s in self.sectors]
		countries = [c for c in select_country if c in self.countries]
		stat = select_stat if select_stat in self.stats else None

		# print(f'Selecting by {select_stat!r} {side!r} {threshold!r}')

		num_sel, num_new = 0, 0
		for c in self.cards:
			if not c.hidden:
				sector, country = c.sector, c.country
				val = c.weight if stat is None and select_stat == 'Weight' else c.features.get(stat)
				if ((len(sectors) and sector in sectors)
						or (len(countries) and country in countries)
						or (val is not None and threshold is not None
							and (val <= threshold if side else val >= threshold))):
					if not c.selected:
						num_new += 1
					c.selected = True
					num_sel += 1

		st.toast(f'Selected {num_sel} stocks ({num_new} new)')


	def _apply_sort(self, group_sector, group_country, group_stat, ascending):
		# st.write(f'Sorting by {group_sector} and {group_country} and {group_stat}')

		sectors = [s for s in group_sector if s in self.sectors]
		countries = [c for c in group_country if c in self.countries]
		stat = group_stat if group_stat in self.stats else None

		def key(card):
			sector, country = card.sector, card.country
			terms = []
			if stat is not None:
				val = card.info[stat]
				if val is None:
					val = (-1)**(not ascending) * float('inf')
				terms.append(val)
			if len(sectors):
				terms.append(tuple(sector == s for s in sectors))
			if len(countries):
				terms.append(tuple(country == c for c in countries))
			return tuple(terms)
		self.cards.sort(key=key, reverse=not ascending)
		for i, card in enumerate(self.cards):
			card.info['order'] = i


	# def _change_delta(self):
	# 	self.delta = st.session_state.delta

	def _update_selected(self, delta):
		return self.update_weights({c: delta for c in self.cards if not c.hidden and not c.locked and c.selected})


	def display(self):
		# control_col, viz_col = st.columns([1, 2 if st.session_state.sidebar_state == 'expanded' else 5])

		new_world_path = None

		# with control_col:
		with st.sidebar:

			ctab, ftab = st.tabs(['Controls', 'Checkpointing'])

			with ctab:
				# st.header(f'Controls')
				st.subheader('Change 🔶')
				col1, col2, col3 = st.columns([4, 1, 1])
				with col1:
					delta = st.slider('Weight', 0., self.max_weight / 5, self.max_weight / 40,
									  label_visibility='collapsed')
				with col2:
					inc = st.button('🔼', help='Increase selected')
				with col3:
					dec = st.button('🔽', help='Decrease selected')
				if inc or dec:
					self._update_selected((-1)**dec * delta)

				col1, col2, col3, col4 = st.columns(4)
				with col1:
					if st.button('🔶 all', help='Select all'):
						self._select_all()
				with col2:
					if st.button('⬛ all', help='Deselect all'):
						self._deselect_all()
				with col3:
					st.button('🔄 all', help='Invert selection', on_click=self._invert_selection)
				with col4:
					st.button('👀 all', help='Show all hidden', on_click=self._show_all) # 👁

				col1, col2, col3, col4 = st.columns(4)
				with col1:
					st.button('🔒🔶', help='Lock selected', on_click=self._lock_selected)
				with col2:
					st.button('🔓🔶', help='Unlock selected', on_click=self._unlock_selected)
				with col3:
					st.button('💭🔶', help='Hide selected', on_click=self._hide_selected)
				with col4:
					st.button('🔒💭', help='Lock all hidden', on_click=self._lock_hidden)

				hidden = [c for c in self.cards if c.hidden]
				selected = [c for c in self.cards if c.selected]
				st.write(f'Showing {len(self.cards) - len(hidden)} of {len(self.cards)} stocks '
						 f'({len(selected)} selected).')

				col1, col2, col3, col4 = st.columns([2,1,1,1])
				with col1:
					st.subheader(f'Sort')
				with col2:
					ascending = st.checkbox('⬆️')#, help='Sort ascending/descending')
				with col3:
					if st.button('💰', help='Sort by weight'):
						self.cards.sort(key=lambda c: c.weight, reverse=not ascending)
						for i, card in enumerate(self.cards):
							card.info['order'] = i
				with col4:
					if st.button('🔶', help='Sort by selected'):
						self.cards.sort(key=lambda c: c.selected, reverse=not ascending)
						for i, card in enumerate(self.cards):
							card.info['order'] = i
				with st.expander('Advanced Sort'):
					with st.form('sort_form', clear_on_submit=True):
						# col1, col2 = st.columns([1,2])
						sort_cards = st.form_submit_button('Apply')

						group_sector = st.multiselect('Group sector', self.sectors, key='group_sector')
						group_country = st.multiselect('Group country', self.countries, key='group_country')
						group_stat = st.selectbox('by Stat', ['', *self.stats], key='group_stat')

				if sort_cards:
					self._apply_sort(group_sector, group_country, group_stat, ascending)

				# st.subheader(f'Selection')
				with st.expander('Selection'):
					with st.form('select_form', clear_on_submit=True):
						select_cards = st.form_submit_button('Apply')

						select_sectors = st.multiselect('Select sectors', self.sectors)
						select_country = st.multiselect('Select country', self.countries)

						d_col, q_col = st.columns([2, 1])
						with d_col:
							select_stat = st.selectbox('Feature', ['Weight', *self.stats])
						with q_col:
							ceiling = st.checkbox('↗️', )#label_visibility='collapsed')
						threshold = st.number_input('Weight', 0., self.max_weight, None, label_visibility='collapsed')

				if select_cards:
					self._apply_selection(select_sectors, select_country, select_stat, not ceiling, threshold)

				for card in sorted(self.cards, key=lambda c: c.info['order']):
					if not card.hidden:
						card.display()

			with ftab:
				st.header('Checkpointing')

				with st.form('save', clear_on_submit=True):
					st.subheader('Save')
					include_hidden = st.checkbox('Include hidden')
					include_sector = st.checkbox('Include sectors', value=True)
					include_country = st.checkbox('Include countries', value=True)
					overwrite = st.checkbox('Overwrite')

					filename = st.text_input('Filename', value='default')

					if st.form_submit_button('Save'):
						path = _dis_root / f'{filename}.yaml'
						if path.exists() and not overwrite:
							st.error(f'File {path} already exists (set "overwrite" to overwrite)')
						else:
							self.world.export(path, include_hidden=include_hidden, include_sector=include_sector,
										 include_country=include_country)

				with st.form('load', clear_on_submit=True):
					st.subheader('Load')

					filename = st.text_input('Filename', value='default')

					if st.form_submit_button('Load'):
						path = _dis_root / f'{filename}.yaml'
						if not path.exists():
							st.error(f'File {path} does not exist')
						else:
							new_world_path = path

		return new_world_path


class Card:
	def __init__(self, info, features):
		self.info = info
		self.features = features
		self.p = None
		# self.weight = 1.
		self.max_weight = 100.

	@property
	def name(self):
		return self.info['company_name']
		# return self.info['ticker']

	@property
	def sector(self):
		return str(self.info['sector'])

	@property
	def country(self):
		return str(self.info['country'])

	@property
	def weight(self):
		return self.info['weight']
	@weight.setter
	def weight(self, value):
		self.info['weight'] = value

	@property
	def locked(self):
		return self.info['locked']
	@locked.setter
	def locked(self, value):
		self.info['locked'] = value

	@property
	def selected(self):
		return self.info['sel']
	@selected.setter
	def selected(self, value):
		self.info['sel'] = value

	@property
	def hidden(self):
		return self.info['hidden']
	@hidden.setter
	def hidden(self, value):
		self.info['hidden'] = value

	def set_portfolio(self, portfolio):
		self.p = portfolio

	def update_weight(self):
		self.p.update_weights({self: float(st.session_state[f'weight_{self.name}']) - self.weight})
		# return self.weight

	def display(self):
		with st.container():
			title = self.name
			terms = []
			if self.country in country_flags:
				terms.append(country_flags[self.country])
			if self.sector in sector_emojis:
				terms.append(sector_emojis[self.sector])
			terms.append(self.name)
			title = ' '.join(terms)

			# with st.expander(title):
			# 	st.write(f'Details for {self.info["company_name"]}')
			st.subheader(title)

			s_col, w_col, l_col = st.columns([1, 3, 1])

			with s_col:
				selected = st.checkbox('🔶', value=self.selected, key=f'select_{self.name}', label_visibility='collapsed')
				self.selected = st.session_state[f'select_{self.name}']
				# print(f'{self.name} {selected} {self.selected} {st.session_state[f"select_{self.name}"]}')
				# if selected != st.session_state[f'select_{self.name}']:
				# 	self.selected = selected
				# 	st.rerun()

			with l_col:
				locked = st.checkbox('🔒', value=self.locked, key=f'lock_{self.name}', label_visibility='collapsed')
				self.locked = st.session_state[f'lock_{self.name}']
			# if locked != st.session_state[f'lock_{self.name}']:
				# 	self.locked = st.session_state[f'lock_{self.name}']
				# 	st.rerun()

			with w_col:
				st.slider('Weight', 0., self.max_weight,
										self.weight,
										key=f'weight_{self.name}',
										disabled=self.locked, on_change=self.update_weight, label_visibility='collapsed')
				# self.weight = st.session_state[f'weight_{self.name}']

				# st.markdown(f'<p style="color:#333;">{self.name}</p>', unsafe_allow_html=True)

				# st.button('🔓' if self.locked else '🔒', key=f'lock_{self.name}', on_click=self.toggle_lock)

			# st.divider()











